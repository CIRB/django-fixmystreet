window.onload = function() {
    function today() {
        var today = new Date();
        var dd = today.getDate();
        var mm = today.getMonth()+1; //January is 0!
        var yyyy = today.getFullYear();

        return yyyy + "_" + mm + "_" + dd;
    }
    document.querySelector('#export-csv').onclick = function() {
        // Init vars
        var csv = '"';
        var colDelim = '";"';
        var rowDelim = '"\r\n"';
        var filename = "FMS-" + today() +".csv";

        // Get visible rows
        var rows = table[0].rows;

        // Each rows = csv line
        var counter = -1; //this counter is needed because IE sucks and we can't just use idRow to check if current row is the filter row (to skip it).
        for (idRow in rows) {
            counter++;
            // Skip filter row
            if (counter == 1){
                continue;
            }
            var row = rows[idRow];
            var line = '';

            // Each cells = csv columns
            for (idCell in row.cells) {
                var cell = row.cells[idCell];

                // Skip invisible columns
                if (cell.textContent != undefined) {
                    line += cell.textContent + colDelim;
                }
            }
            // TODO: Add link of the report in the ending cell

            // Copy line to csv
            csv += line + rowDelim;
        }

        // Encode data : '%EF%BB%BF' is the BOM necessary for the file to be opened correctly in Excel. Otherwise
        // special characters are display incorrectly.
        csvData = 'data:text/csv;charset=utf-8,%EF%BB%BF' + encodeURIComponent(csv);

        // Download
        var virtualLink = document.createElement("a");

        if (virtualLink.download !== undefined) {
            // Browsers that support HTML5 download attribute
            virtualLink.setAttribute("href", csvData);
            virtualLink.setAttribute("download", filename);
        }
        else if(navigator.msSaveBlob) { // IE 10+
            var blobObject = new Blob(["\ufeff"+csv], {"type":"text/csv;charset=utf-8;"});
            navigator.msSaveBlob(blobObject, filename);
        }

        document.body.appendChild(virtualLink);
        virtualLink.click();
        document.body.removeChild(virtualLink);
    };

};
