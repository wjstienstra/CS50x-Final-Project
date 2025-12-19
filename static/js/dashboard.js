document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('search-input');
    const searchResults = document.getElementById('search-results');

    // Function to show search results
    function showResults() {
        searchResults.style.display = 'block';
    }

    // Function to hide search results
    function hideResults() {
        searchResults.style.display = 'none';
    }

    searchInput.addEventListener('keyup', function() {
        const query = searchInput.value;

        if (query.length < 2) {
            hideResults();
            searchResults.innerHTML = '';
            return;
        }

        fetch(`/search?q=${query}`)
            .then(response => response.json())
            .then(data => {
                searchResults.innerHTML = ''; // Clear old search results

                if (data.length > 0) {
                    data.forEach(company => {
                        // Make a container for each company
                        const resultItem = document.createElement('div');
                        resultItem.style.display = 'flex';
                        resultItem.style.justifyContent = 'space-between';
                        resultItem.style.alignItems = 'center';
                        resultItem.style.padding = '10px';
                        resultItem.style.borderBottom = '1px solid #eee';

                        // Company name and symbol
                        const companyInfo = document.createElement('span');
                        companyInfo.innerHTML = `<strong>${company.symbol}</strong> - ${company.description}`;

                        // Form with "follow" button
                        const followForm = document.createElement('form');
                        followForm.action = '/subscribe';
                        followForm.method = 'post';
                        followForm.innerHTML = `
                            <input type="hidden" name="symbol" value="${company.symbol}">
                            <input type="hidden" name="name" value="${company.description}">
                            <button type="submit" class="btn btn-sm btn-success";">Volgen</button>
                        `;

                        resultItem.appendChild(companyInfo);
                        resultItem.appendChild(followForm);
                        searchResults.appendChild(resultItem);
                    });
                    showResults(); // Show overlay
                } else {
                    hideResults(); // Hide when no results
                }
            });
    });

    // Hide results when user clicks anywhere else.
    document.addEventListener('click', function(event) {
        if (!searchInput.contains(event.target)) {
            hideResults();
        }
    });

    // But prevent hiding, when clicking in the search results.
    searchInput.addEventListener('click', function(event) {
        event.stopPropagation();
    });
});
