document.addEventListener('DOMContentLoaded', () => {
    const backendURL = '/api';
    const authToken = localStorage.getItem('authToken');
    if (!authToken) {
        window.location.href = '/login';
        return;
    }

    let allIngredients = [];
    let currentUserIngredients = new Set();
    let originalRecipeData = null;

    // --- DOM REFERENCES ---
    const masterDetailContainer = document.getElementById('masterDetailContainer');
    const detailView = document.getElementById('detailView');
    const ingredientForm = document.getElementById("ingredientForm");
    const ingredientList = document.getElementById("ingredientList");
    const ingredientDatalist = document.getElementById("ingredient-datalist");
    const addIngredientBtn = document.getElementById("addIngredient");
    const generateBtn = document.getElementById("generateBtn");
    const resultsWrapper = document.getElementById("resultsWrapper");
    const imageUploadInput = document.getElementById('imageUploadInput');
    const imageUploadBtn = document.getElementById('imageUploadBtn');
    const imageUploadSpinner = document.getElementById('imageUploadSpinner');
    const profileBtn = document.getElementById('profileBtn');
    const favoritesBtn = document.getElementById('favoritesBtn');
    const homeBtn = document.getElementById('homeBtn');
    const discoverBtn = document.getElementById('discoverBtn');
    const profileDropdownMenu = document.getElementById('profileDropdownMenu');
    const suggestionsBtn = document.getElementById('suggestionsBtn');
    const dietaryFilter = document.getElementById('dietaryFilter');
    const difficultyFilter = document.getElementById('difficultyFilter');
    const timeFilter = document.getElementById('timeFilter');

    // --- HELPER & AUTH FUNCTIONS ---
    function parseJwt(token) {
        try {
            return JSON.parse(atob(token.split('.')[1]));
        } catch (e) {
            return null;
        }
    }

    function handleLogout() {
        localStorage.removeItem('authToken');
        window.location.href = '/login';
    }

    // --- INITIALIZATION ---
    const userInfo = parseJwt(authToken);
    if (userInfo) {
        const dropdownUserName = document.getElementById('dropdownUserName');
        const dropdownUserEmail = document.getElementById('dropdownUserEmail');
        if (dropdownUserName) dropdownUserName.textContent = userInfo.name;
        if (dropdownUserEmail) dropdownUserEmail.textContent = userInfo.email;
    } else {
        handleLogout();
    }

    async function fetchWithAuth(endpoint, options = {}) {
        const headers = {
            'Authorization': `Bearer ${authToken}`,
            ...options.headers
        };
        if (!(options.body instanceof FormData)) {
            headers['Content-Type'] = 'application/json';
        }
        const response = await fetch(`${backendURL}${endpoint}`, {
            ...options,
            headers
        });
        if (response.status === 401 || response.status === 403) {
            showToast('Session expired. Please log in again.', 'error');
            setTimeout(handleLogout, 2000);
            throw new Error('Unauthorized');
        }
        return response;
    }

    // --- VIEW & RENDER FUNCTIONS ---
    function showListView() {
        masterDetailContainer.classList.remove('detail-view-open');
        document.querySelectorAll('.recipe-card.selected').forEach(card => card.classList.remove('selected'));
        setTimeout(() => {
            detailView.innerHTML = '';
        }, 300);
    }

    function showDetailView() {
        masterDetailContainer.classList.add('detail-view-open');
    }

    function renderResults(recipes, title = 'Generated Recipes') {
        if (!recipes || recipes.length === 0) {
            resultsWrapper.innerHTML = `<div class="card empty-state"><p>No matching recipes found. Try different ingredients or filters!</p></div>`;
            return;
        }
        const recipeCardsHTML = recipes.map(r => {
            const metaItems = [];
            if (r.cuisine) metaItems.push(`<span>${r.cuisine}</span>`);
            if (r.difficulty) metaItems.push(`<span><b>Difficulty:</b> ${r.difficulty}</span>`);
            if (r.cook_time) metaItems.push(`<span><b>Cook Time:</b> ${r.cook_time} mins</span>`);
            if (r.substitutions && Object.keys(r.substitutions).length > 0) {
                metaItems.push(`<span class="substitution-badge">⚠️ Substitutes</span>`);
            }
            const subsData = r.substitutions ? JSON.stringify(r.substitutions) : '';
            return `
                <div class="recipe-card" data-recipe-name="${r.name}" data-substitutions='${subsData}'>
                    <img src="${r.image_url || 'https://via.placeholder.com/150'}" alt="${r.name}" class="recipe-card-image">
                    <div class="recipe-card-content">
                        <h3>${r.name}</h3>
                        <div class="meta">${metaItems.join(' <span class="text-muted">&bull;</span> ')}</div>
                    </div>
                </div>`;
        }).join("");
        resultsWrapper.innerHTML = `<section class="card results-container"><h2>${title}</h2><div class="recipe-list">${recipeCardsHTML}</div></section>`;
    }

    function renderRecipeDetail(recipe, substitutions) {
        originalRecipeData = {
            ...recipe
        };

        const servingsHTML = `
            <div class="servings-section">
                <h3>Servings</h3>
                <div class="servings-adjuster">
                    <button id="decreaseServings" type="button">-</button>
                    <span id="servings-display">${recipe.servings}</span>
                    <button id="increaseServings" type="button">+</button>
                </div>
            </div>`;

        const ratingHTML = `
            <div class="rating-section">
                <h3>Rate this Recipe</h3>
                <div class="star-rating" data-recipe-name="${recipe.name}">
                    <span class="star" data-value="5">&#9733;</span>
                    <span class="star" data-value="4">&#9733;</span>
                    <span class="star" data-value="3">&#9733;</span>
                    <span class="star" data-value="2">&#9733;</span>
                    <span class="star" data-value="1">&#9733;</span>
                </div>
                <div class="rating-summary" id="ratingSummary">Loading rating...</div>
            </div>`;

        const ingredientsHTML = Object.entries(recipe.ingredients).map(([name, amount]) => {
            const formattedName = name.split(' ').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
            let subNote = '';
            for (const original in substitutions) {
                if (substitutions[original] === name) {
                    const formattedOriginal = original.charAt(0).toUpperCase() + original.slice(1);
                    subNote = ` <span class="substitution-note">(for ${formattedOriginal})</span>`;
                }
            }
            return `<li data-original-amount="${amount}">${formattedName}${subNote} <span>${Math.round(amount)}g</span></li>`;
        }).join('');

        const recipeIngredients = Object.keys(recipe.ingredients);
        const missingIngredients = recipeIngredients.filter(ing => !currentUserIngredients.has(ing) && !Object.values(substitutions).includes(ing));
        let missingIngredientsHTML = '';
        if (missingIngredients.length > 0) {
            const missingList = missingIngredients.map(ingName => {
                const amount = recipe.ingredients[ingName];
                const formattedName = ingName.split(' ').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
                return `<li>${formattedName} <span>${Math.round(amount)}g</span></li>`;
            }).join('');
            missingIngredientsHTML = `
                <div class="missing-ingredients-section">
                    <h3>You Will Also Need</h3>
                    <ul class="ingredients-list">${missingList}</ul>
                </div>`;
        }

        const nutritionHTML = recipe.nutrition ? Object.entries(recipe.nutrition).map(([key, value]) => {
            const unit = key.toLowerCase() === 'calories' ? '' : 'g';
            const formattedKey = key.charAt(0).toUpperCase() + key.slice(1);
            return `<li><strong>${formattedKey}</strong> ${value}${unit}</li>`;
        }).join('') : '<li>Not available</li>';

        const stepsHTML = recipe.steps.map(step => `<li>${step}</li>`).join('');

        detailView.innerHTML = `
            <button class="close-detail-btn"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" width="24"><path d="M6.28 5.22a.75.75 0 00-1.06 1.06L8.94 10l-3.72 3.72a.75.75 0 101.06 1.06L10 11.06l3.72 3.72a.75.75 0 101.06-1.06L11.06 10l3.72-3.72a.75.75 0 00-1.06-1.06L10 8.94 6.28 5.22z" /></svg></button>
            <div class="card">
                 <header class="recipe-detail-header"><h2>${recipe.name}</h2></header>
                 <img src="${recipe.image_url || 'https://via.placeholder.com/800x400'}" alt="${recipe.name}" class="recipe-detail-image">
                 ${servingsHTML}
                 ${ratingHTML}
                 <div class="ingredients-section">
                     <h3>Ingredients</h3>
                     <ul class="ingredients-list">${ingredientsHTML}</ul>
                 </div>
                 ${missingIngredientsHTML}
                 <div class="nutrition-section">
                     <h3>Nutrition</h3>
                     <ul class="nutrition-list">${nutritionHTML}</ul>
                 </div>
                 <div class="steps-section">
                     <h3>Instructions</h3>
                     <ol class="steps-list">${stepsHTML}</ol>
                 </div>
                 <div class="detail-actions">
                      <button class="btn-primary fav-btn" data-name="${recipe.name}">Add to Favorites</button>
                 </div>
            </div>`;

        detailView.querySelector('.close-detail-btn').addEventListener('click', showListView);
        document.getElementById('decreaseServings').addEventListener('click', () => updateServings(-1));
        document.getElementById('increaseServings').addEventListener('click', () => updateServings(1));
        fetchAndDisplayRatings(recipe.name);
        detailView.querySelector('.star-rating').addEventListener('click', handleStarClick);
    }

    // --- FEATURE LOGIC ---
    function updateServings(change) {
        const display = document.getElementById('servings-display');
        let currentServings = parseInt(display.textContent);
        const newServings = Math.max(1, currentServings + change);
        if (newServings === currentServings) return;
        display.textContent = newServings;

        const originalServings = originalRecipeData.servings;
        const ingredientsList = detailView.querySelector('.ingredients-list');

        ingredientsList.querySelectorAll('li[data-original-amount]').forEach(li => {
            const originalAmount = parseFloat(li.dataset.originalAmount);
            const amountPerServing = originalAmount / originalServings;
            const newAmount = Math.round(amountPerServing * newServings);
            li.querySelector('span').textContent = `${newAmount}g`;
        });
    }

    async function fetchAndDisplayRatings(recipeName) {
        try {
            const res = await fetchWithAuth(`/recipe/${recipeName}/ratings`);
            if (!res.ok) throw new Error('Could not load ratings');
            const data = await res.json();
            const summaryEl = document.getElementById('ratingSummary');
            if (data.rating_count > 0) {
                summaryEl.textContent = `Average: ${data.average_rating.toFixed(1)} / 5 (from ${data.rating_count} ratings)`;
            } else {
                summaryEl.textContent = 'Be the first to rate this recipe!';
            }
            updateStarDisplay(data.user_rating);
        } catch (error) {
            document.getElementById('ratingSummary').textContent = 'Could not load rating.';
        }
    }

    async function handleStarClick(event) {
        if (!event.target.classList.contains('star')) return;
        const rating = parseInt(event.target.dataset.value);
        const recipeName = event.currentTarget.dataset.recipeName;
        updateStarDisplay(rating);
        try {
            await fetchWithAuth('/rate', {
                method: 'POST',
                body: JSON.stringify({
                    recipe_name: recipeName,
                    rating: rating
                }),
            });
            showToast('Your rating has been saved!', 'success');
            fetchAndDisplayRatings(recipeName);
        } catch (error) {
            showToast('Failed to save your rating.', 'error');
        }
    }

    function updateStarDisplay(rating) {
        const stars = detailView.querySelectorAll('.star-rating .star');
        stars.forEach(star => {
            star.classList.toggle('selected', parseInt(star.dataset.value) <= rating);
        });
    }

    // --- DATA FETCHING & NAVIGATION ---
    async function fetchAndShowSuggestions() {
        updateActiveNav(suggestionsBtn);
        resultsWrapper.innerHTML = `<div class="card"><div class="spinner" style="display:block; margin: 80px auto; width: 40px; height: 40px;"></div></div>`;
        showListView();
        try {
            const res = await fetchWithAuth('/suggestions');
            if (!res.ok) throw new Error('Could not get suggestions.');
            const data = await res.json();
            if (data.recipes.length === 0) {
                resultsWrapper.innerHTML = `<div class="card empty-state"><p>Rate more recipes with 3+ stars to get personalized suggestions!</p></div>`;
            } else {
                renderResults(data.recipes, 'Suggested For You');
            }
        } catch (error) {
            showToast(error.message, 'error');
            resultsWrapper.innerHTML = '';
        }
    }

    function updateActiveNav(activeButton) {
        [homeBtn, discoverBtn, suggestionsBtn, favoritesBtn].forEach(btn => btn?.classList.remove('active'));
        if (activeButton) {
            activeButton.classList.add('active');
        }
    }

    async function fetchAndShowAllRecipes() {
        updateActiveNav(discoverBtn);
        resultsWrapper.innerHTML = `<div class="card"><div class="spinner" style="display:block; margin: 80px auto; width: 40px; height: 40px;"></div></div>`;
        showListView();
        try {
            const res = await fetchWithAuth('/all');
            if (!res.ok) throw new Error('Could not fetch recipes.');
            const data = await res.json();
            renderResults(data.recipes, 'Discover Recipes');
        } catch (error) {
            showToast(error.message, 'error');
            resultsWrapper.innerHTML = '';
        }
    }

    async function fetchAndShowFavorites() {
        updateActiveNav(favoritesBtn);
        resultsWrapper.innerHTML = `<div class="card"><div class="spinner" style="display:block; margin: 80px auto; width: 40px; height: 40px;"></div></div>`;
        showListView();
        try {
            const res = await fetchWithAuth('/favorites');
            if (!res.ok) throw new Error('Could not fetch your favorites.');
            const data = await res.json();
            renderResults(data.recipes, 'Your Favorite Recipes');
        } catch (error) {
            showToast(error.message, 'error');
            resultsWrapper.innerHTML = '';
        }
    }

    async function fetchAndShowRecipeDetails(recipeName, clickedCard) {
        document.querySelectorAll('.recipe-card.selected').forEach(card => card.classList.remove('selected'));
        if (clickedCard) clickedCard.classList.add('selected');
        const substitutions = JSON.parse(clickedCard.dataset.substitutions || '{}');
        showDetailView();
        detailView.innerHTML = `<div class="card"><div class="spinner" style="display:block; margin: 80px auto; width: 40px; height: 40px;"></div></div>`;
        try {
            const res = await fetchWithAuth(`/recipe/${encodeURIComponent(recipeName)}`);
            if (!res.ok) throw new Error('Recipe not found');
            const data = await res.json();
            renderRecipeDetail(data, substitutions);
        } catch (error) {
            showToast(error.message, 'error');
            showListView();
        }
    }

    // --- CORE GENERATION AND EVENT LISTENERS ---
    async function generateAndFilterRecipes() {
        const ingredientRows = document.querySelectorAll(".ingredient-row");
        const hasIngredients = Array.from(ingredientRows).some(row => row.querySelector('.ingredient-input').value.trim() !== '');

        if (!hasIngredients) {
            resultsWrapper.innerHTML = '';
            return;
        }

        updateActiveNav(homeBtn);
        toggleButtonLoading(generateBtn, true);
        resultsWrapper.innerHTML = `<div class="card"><div class="spinner" style="display:block; margin: 80px auto; width: 40px; height: 40px;"></div></div>`;

        const dietary = dietaryFilter.value;
        const difficulty = difficultyFilter.value;
        const maxTime = timeFilter.value;

        const params = new URLSearchParams();
        if (dietary !== 'all') params.append('dietary', dietary);
        if (difficulty !== 'all') params.append('difficulty', difficulty);
        if (maxTime) params.append('max_time', maxTime);
        const queryString = params.toString() ? `?${params.toString()}` : '';

        const ingredients = {};
        const addedIngredients = new Set();
        let hasError = false;

        ingredientRows.forEach(row => {
            if (hasError) return;
            const input = row.querySelector(".ingredient-input");
            const ing = input.value.trim().toLowerCase();
            if (ing) {
                if (!allIngredients.map(i => i.toLowerCase()).includes(ing)) {
                    showToast(`'${input.value}' is not a valid ingredient.`, "error");
                    hasError = true;
                    return;
                }
                if (addedIngredients.has(ing)) {
                    showToast(`'${input.value}' has been added more than once.`, "error");
                    hasError = true;
                    return;
                }
                ingredients[ing] = 1;
                addedIngredients.add(ing);
            }
        });

        if (hasError || Object.keys(ingredients).length === 0) {
            if (!hasError) showToast("Please add at least one ingredient.", "error");
            toggleButtonLoading(generateBtn, false);
            resultsWrapper.innerHTML = '';
            return;
        }

        currentUserIngredients = new Set(Object.keys(ingredients));

        try {
            const res = await fetchWithAuth(`/generate${queryString}`, {
                method: 'POST',
                body: JSON.stringify({
                    ingredients
                }),
            });
            if (!res.ok) throw new Error('Failed to get recipes');
            const data = await res.json();
            renderResults(data.recipes, "Generated Recipes");
        } catch (error) {
            showToast(error.message, 'error');
            resultsWrapper.innerHTML = '';
        } finally {
            toggleButtonLoading(generateBtn, false);
        }
    }

    function addIngredientRow(ingredientValue = '') {
        const row = document.createElement("div");
        row.className = "ingredient-row";
        row.innerHTML = `
            <input class="ingredient-input" list="ingredient-datalist" placeholder="Type or select an ingredient..." value="${ingredientValue}">
            <input type="number" class="quantity-input" placeholder="Quantity (g)" min="1">
            <button type="button" class="remove-btn"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" width="20"><path fill-rule="evenodd" d="M8.75 1A2.75 2.75 0 0 0 6 3.75v.443c-1.15.048-2.26.11-3.35.19-1.2.09-1.9.99-1.9 2.18v.28c0 .28.22.5.5.5h17a.5.5 0 0 0 .5-.5v-.28c0-1.19-.7-2.09-1.9-2.18-.36-.03-.72-.05-1.08-.07a.75.75 0 0 0-.74.65c-.03.21-.06.41-.1.62h-4.3c-.04-.21-.07-.41-.1-.62a.75.75 0 0 0-.74-.65c-.36.02-.72.04-1.08.07-1.09.08-2.19.14-3.35.19V3.75A2.75 2.75 0 0 0 8.75 1ZM4.25 8.5V16a1.5 1.5 0 0 0 1.5 1.5h8.5a1.5 1.5 0 0 0 1.5-1.5V8.5h-11.5Z" clip-rule="evenodd" /></svg></button>`;
        ingredientList.appendChild(row);
        row.querySelector(".remove-btn").addEventListener("click", () => row.remove());
    }

    // --- EVENT LISTENERS ---
    if (profileBtn) {
        profileBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            profileDropdownMenu.classList.toggle('show');
        });
    }
    if (profileDropdownMenu) {
        profileDropdownMenu.addEventListener('click', (e) => {
            if (e.target.id === 'logoutBtn') {
                e.preventDefault();
                handleLogout();
            }
        });
    }
    window.addEventListener('click', () => {
        if (profileDropdownMenu?.classList.contains('show')) {
            profileDropdownMenu.classList.remove('show');
        }
    });
    [homeBtn, discoverBtn, suggestionsBtn, favoritesBtn].forEach(btn => {
        if (btn) {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const id = e.currentTarget.id;
                if (id === 'homeBtn') window.location.reload();
                if (id === 'discoverBtn') fetchAndShowAllRecipes();
                if (id === 'suggestionsBtn') fetchAndShowSuggestions();
                if (id === 'favoritesBtn') fetchAndShowFavorites();
            });
        }
    });

    detailView.addEventListener('click', async (e) => {
        if (e.target.classList.contains('fav-btn')) {
            const button = e.target;
            button.disabled = true;
            button.textContent = 'Saving...';
            try {
                const res = await fetchWithAuth('/favorites', {
                    method: 'POST',
                    body: JSON.stringify({
                        recipe_name: button.dataset.name
                    })
                });
                if (!res.ok) {
                    const data = await res.json();
                    throw new Error(data.message);
                }
                showToast('Recipe added to favorites!', 'success');
                button.textContent = 'Favorited!';
            } catch (error) {
                showToast(error.message, 'error');
                button.disabled = false;
                button.textContent = 'Add to Favorites';
            }
        }
    });

    addIngredientBtn.addEventListener("click", () => addIngredientRow());
    ingredientForm.addEventListener("submit", (e) => {
        e.preventDefault();
        generateAndFilterRecipes();
    });
    [dietaryFilter, difficultyFilter, timeFilter].forEach(filter => {
        if (filter) {
            filter.addEventListener('change', generateAndFilterRecipes);
        }
    });
    resultsWrapper.addEventListener('click', (e) => {
        const card = e.target.closest('.recipe-card');
        if (card) {
            fetchAndShowRecipeDetails(card.dataset.recipeName, card);
        }
    });
    if (imageUploadBtn) {
        imageUploadBtn.addEventListener('click', () => imageUploadInput.click());
        imageUploadInput.addEventListener('change', async (e) => {
            const file = event.target.files[0];
            if (!file) return;
            imageUploadBtn.disabled = true;
            imageUploadSpinner.style.display = 'block';
            const formData = new FormData();
            formData.append('image', file);
            try {
                const res = await fetchWithAuth('/recognize-ingredients', {
                    method: 'POST',
                    body: formData
                });
                const data = await res.json();
                if (!res.ok) throw new Error(data.message || 'Recognition failed');
                data.recognized_ingredients.forEach(addRecognizedIngredient);
                showToast('Ingredients added from image!', 'success');
            } catch (error) {
                showToast(error.message, 'error');
            } finally {
                imageUploadBtn.disabled = false;
                imageUploadSpinner.style.display = 'none';
                imageUploadInput.value = '';
            }
        });
    }

    function addRecognizedIngredient(ingredientName) {
        const isAlreadyAdded = Array.from(document.querySelectorAll('.ingredient-input')).some(input => input.value.toLowerCase() === ingredientName);
        if (!isAlreadyAdded) {
            const displayName = ingredientName.charAt(0).toUpperCase() + ingredientName.slice(1);
            addIngredientRow(displayName);
            currentUserIngredients.add(ingredientName.toLowerCase());
        }
    }

    // --- FINAL INITIALIZATION ---
    async function initializeApp() {
        try {
            const res = await fetchWithAuth('/ingredients');
            if (!res.ok) throw new Error('Could not fetch ingredients');
            const data = await res.json();
            allIngredients = data.ingredients.map(i => i.charAt(0).toUpperCase() + i.slice(1));
            ingredientDatalist.innerHTML = allIngredients.map(ing => `<option value="${ing}"></option>`).join('');
        } catch (error) {
            showToast('Could not connect to the server.', 'error');
        }
    }

    function showToast(message, type = 'error') {
        const c = document.getElementById('toastContainer');
        const t = document.createElement('div');
        t.className = `toast ${type}`;
        t.textContent = message;
        c.appendChild(t);
        setTimeout(() => t.remove(), 4000);
    }

    function toggleButtonLoading(button, isLoading) {
        const s = button.querySelector('.spinner');
        const t = button.querySelector('span');
        if (button) button.disabled = isLoading;
        if (s) s.style.display = isLoading ? 'block' : 'none';
        if (t) t.style.display = isLoading ? 'none' : 'inline';
    }
    initializeApp();
});

