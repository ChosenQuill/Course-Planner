(async () => {
    // Helper to pause briefly so DOM can update after clicking "Next"
    function sleep(ms) {
      return new Promise(resolve => setTimeout(resolve, ms));
    }
  
    // Extract the table rows from the DOM and build an array of data
    function scrapeTableData() {
      const rows = document.querySelectorAll('table tbody tr');
      const pageData = [];
  
      rows.forEach((row) => {
        const cells = row.querySelectorAll('td');
        if (cells.length >= 6) {
          const courseName = cells[0]
            .querySelector('span.text-base')
            ?.innerText
            .trim() || '';
          const codes      = cells[1].innerText.trim();
          const rating     = Number(cells[2].innerText.trim());
          const difficulty = Number(cells[3].innerText.trim());
          const workload   = Number(cells[4].innerText.trim());
          const numReviews = Number(cells[5].innerText.trim());
          const interest = 5;
          pageData.push({
            courseName,
            codes,
            rating,
            difficulty,
            workload,
            numReviews,
            interest
          });
        }
      });
      return pageData;
    }
  
    function getNextButton() {
      return document.querySelector(
        'nav[aria-label="Pagination"] button:last-child'
      );
    }
  
    function isNextDisabled(btn) {
      return !btn || btn.hasAttribute('disabled') || btn.disabled;
    }
  
    // Main script
    const allCourses = [];
    
    while (true) {
      // Scrape the current page
      const thisPageData = scrapeTableData();
      allCourses.push(...thisPageData);
  
      // Check if "Next" is disabled (ie no more pages)
      const nextBtn = getNextButton();
      if (isNextDisabled(nextBtn)) {
        break;
      }
  
      // Click "Next", wait for page to re-render
      nextBtn.click();
      await sleep(200);
    }
  
    // Done. Print concatenated results.
    console.log('All scraped data:', allCourses);
  })();