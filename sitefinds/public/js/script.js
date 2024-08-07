var $table = $('#table')
var $button = $('#button')
var mapFindSpot = null;
var mapMint = null;
var TOKEN = 'pk.eyJ1IjoiaW1yYW5hc2lmIiwiYSI6ImNseDBjaTNtbTA1dDcyaXNjdjJsa2tlbWIifQ.2_kCycbjY-7_LrlucTewZw';
var selectedDropdowns = {};

var visibleColumns = ['Reference', 'Findspot', 'Mint', 'ARCH coin type', 'Metal', 'Production From Date', 'Production To Date', 'Find Region']
var totalRows = 0;

function detailFormatter(index, row) {
    var html = []
    $.each(row, function (key, value) {
        if (!visibleColumns.includes(key) && value !== '') {
            let v = urlFormatter(value);
            html.push('<p><b>' + key + ':</b> ' + v + '</p>')
        }
    })
    return html.join('')
}

function urlFormatter(value, row) {
    if (value !== "" && value.toString().includes('http'))
        return `<a href="${value}" target="_blank">${value} <i class="fas fa-external-link-alt"></i></a>`;

    return value;
}

$(function () {
    function loadMap() {
        let json_data = updateTable($table.bootstrapTable('getData'))
        if (totalRows === 0) totalRows = json_data.length

        if (totalRows !== json_data.length) $('.export').removeClass('d-none')
        else if (totalRows === json_data.length) $('.export').addClass('d-none')

        //console.log(json_data.length)
        let findSpotLatLng = []
        let mintLatLng = []

        for (let item of json_data) {
            if (item.Lat !== undefined && item.Lat !== null && item.Lat !== '') {
                if (findSpotLatLng.filter(x => x.lat === item.Lat && x.long === item.Long).length === 0) {
                    findSpotLatLng.push({
                        lat: item.Lat,
                        long: item.Long,
                        data: [{
                            Reference: item.Reference,
                            Pleiades: item.Pleiades,
                            Findspot: item.Findspot,
                            date_from: item['Production From Date'],
                            date_to: item['Production To Date'],
                        }]
                    })
                }
                else {
                    let itemFound = findSpotLatLng.find(x => x.lat === item.Lat && x.long === item.Long)
                    itemFound.data.push({
                        Reference: item.Reference,
                        Pleiades: item.Pleiades,
                        Findspot: item.Findspot,
                        date_from: item['Production From Date'],
                        date_to: item['Production To Date'],
                    })
                }
            }
            ////////////////////////////////////////////////////////////////////////////
            /// Mint Map
            if (item['Mint Lat'] !== undefined && item['Mint Lat'] !== null && item['Mint Lat'] !== '') {
                if (mintLatLng.filter(x => x.lat === item['Mint Lat'] && x.long === item['Mint Long']).length === 0) {
                    mintLatLng.push({
                        lat: item['Mint Lat'],
                        long: item['Mint Long'],
                        data: [{
                            Reference: item.Reference,
                            Nomisma_mint_ID: item["Nomisma mint ID"],
                            Mint: item.Mint,
                            date_from: item['Production From Date'],
                            date_to: item['Production To Date'],
                        }]
                    })
                }
                else {
                    let itemFound = mintLatLng.find(x => x.lat === item['Mint Lat'] && x.long === item['Mint Long'])
                    itemFound.data.push({
                        Reference: item.Reference,
                        Nomisma_mint_ID: item["Nomisma mint ID"],
                        Mint: item.Mint,
                        date_from: item['Production From Date'],
                        date_to: item['Production To Date'],
                    })
                }
            }
        }

        //////////////////////////////////
        /// FindSpot Map and Display marker with popups
        if (findSpotLatLng.length > 0) {
            if (mapFindSpot !== null) {
                mapFindSpot.off();
                mapFindSpot.remove();
            }
            mapFindSpot = L.map('mapFindSpot').setView([findSpotLatLng[0].lat, findSpotLatLng[0].long], 6);
            L.tileLayer('https://api.mapbox.com/styles/v1/mapbox/streets-v11/tiles/{z}/{x}/{y}?access_token=' + TOKEN, {
                attribution: '&copy;'
                // tileSize: 512,
                // zoomOffset: -1
            }).addTo(mapFindSpot);

            // Layer group to manage markers
            var markersLayer = L.layerGroup().addTo(mapFindSpot);
            // Clear existing markers
            markersLayer.clearLayers();
            for (let item of findSpotLatLng) {
                let marker = L.marker([item.lat, item.long]).addTo(mapFindSpot);
                let displayItems = `<div class="card border-0 p-0 m-0">
                                    <div class="card-header">
                                       Records (Count: ${item.data.length})
                                    </div>
                                    <ul class="list-group list-group-flush">`;
                for (let d of item.data) {
                    displayItems += `<li class="list-group-item">
                                       <a class="mb-1" title="${d.Findspot}: ${d.date_from} To ${d.date_to} ${d.Reference}" style="display: block;overflow: hidden; text-overflow: ellipsis;white-space: nowrap; width:90%" href="${d.Pleiades}" target="_blank">
                                       ${d.Findspot}: ${d.date_from} To ${d.date_to} ${d.Reference} </a>
                                    </li>`;
                }
                displayItems += `</ul></div>`;

                marker.bindPopup(displayItems, {
                    maxHeight: 150
                });
                markersLayer.addLayer(marker);
            }
        } else {
            // mapFindSpot.off();
            // mapFindSpot.remove();
            mapFindSpot.eachLayer(function (layer) {
                mapFindSpot.removeLayer(layer);
            });
        }

        //////////////////////////////////
        /// FindSpot Map and Display marker with popups
        if (mintLatLng.length > 0) {
            if (mapMint !== null) {
                mapMint.off();
                mapMint.remove();
            }
            mapMint = L.map('mapMint').setView([mintLatLng[0].lat, mintLatLng[0].long], 6);
            L.tileLayer('https://api.mapbox.com/styles/v1/mapbox/streets-v11/tiles/{z}/{x}/{y}?access_token=' + TOKEN, {
                attribution: '&copy;'
                // tileSize: 512,
                // zoomOffset: -1
            }).addTo(mapMint);

            // Layer group to manage markers
            var markersLayerMint = L.layerGroup().addTo(mapMint);
            // Clear existing markers
            markersLayerMint.clearLayers();
            //console.log(mintLatLng)
            for (let item of mintLatLng) {
                let marker = L.marker([item.lat, item.long]).addTo(mapMint);
                let displayItems = `<div class="card border-0 p-0 m-0">
                                    <div class="card-header">
                                       Records (Count: ${item.data.length})
                                    </div>
                                    <ul class="list-group list-group-flush">`;
                for (let d of item.data) {
                    displayItems += `<li class="list-group-item">
                                       <a class="mb-1" title="${d.Mint}: ${d.date_from} To ${d.date_to} ${d.Reference}" style="display: block;overflow: hidden; text-overflow: ellipsis;white-space: nowrap; width:90%" href="${d.Nomisma_mint_ID}" target="_blank">
                                       ${d.Mint}: ${d.date_from} To ${d.date_to} ${d.Reference} </a>
                                    </li>`;
                }
                displayItems += `</ul></div>`;

                marker.bindPopup(displayItems, {
                    maxHeight: 150
                });
                markersLayerMint.addLayer(marker);
            }
        } else {
            // mapFindSpot.off();
            // mapFindSpot.remove();
            mapMint.eachLayer(function (layer) {
                mapMint.removeLayer(layer);
            });
        }

        /////////////////////////
        loadFilters()
    }

    function updateTable(data) {
        if ($('#date_from').val() !== '' && $('#date_to').val() !== '') {
            const fromDate = parseInt($('#date_from').val());
            const toDate = parseInt($('#date_to').val());

            const filteredData = data.filter(item => {
                const productionFromDate = parseInt(item["Production From Date"]);
                const productionToDate = parseInt(item["Production To Date"]);
                return productionFromDate >= fromDate && productionToDate <= toDate;
            });

            $table.bootstrapTable('load', filteredData);
            return filteredData;
        }
        else if ($('#date_from').val() !== '') {
            const fromDate = parseInt($('#date_from').val());

            const filteredData = data.filter(item => {
                const productionFromDate = parseInt(item["Production From Date"]);
                return productionFromDate >= fromDate;
            });

            $table.bootstrapTable('load', filteredData);
            return filteredData;
        }
        else if ($('#date_to').val() !== '') {
            const toDate = parseInt($('#date_to').val());

            const filteredData = data.filter(item => {
                const productionToDate = parseInt(item["Production To Date"]);
                return productionToDate <= toDate;
            });

            $table.bootstrapTable('load', filteredData);
            return filteredData;
        }

        return data;
    }

    $('.search-input').on("keyup", function () {
        let interval = setInterval(() => {
            clearInterval(interval);
            loadMap()
        }, 500);
    });

    $('.search-input').on("input", function () {
        let interval = setInterval(() => {
            clearInterval(interval);
            loadMap()
        }, 500);
    });

    let interval = setInterval(() => {
        if ($table.bootstrapTable('getData').length > 0) {
            clearInterval(interval)
            loadMap();
        }
    }, 500);

    function loadFilters() {
        let json_data = $table.bootstrapTable('getData')
        let findSpots = getFilterWithCount(json_data, 'Findspot');  //[...new Set(json_data.map(item => item['Findspot']))]
        var $select = $('#selFindspot');
        let opt = '';
        for (let fs of findSpots) {
            opt += `<option value="${fs.value}" data-subtext="(${fs.count})">${fs.value}</option>`
        }
        $select.html(opt)

        ///////////////////////////////////////////////

        let mints = getFilterWithCount(json_data, 'Mint');
        $select = $('#selMint');
        opt = '';
        for (let m of mints) {
            opt += `<option value="${m.value}" data-subtext="(${m.count})">${m.value}</option>`
        }
        $select.html(opt)

        /////////////////////////////////////////////////

        let archTypes = getFilterWithCount(json_data, 'ARCH coin type');
        $select = $('#selARCHCoinType');
        opt = '';
        for (let t of archTypes) {
            opt += `<option value="${t.value}" data-subtext="(${t.count})">${t.value.split('/').pop()}</option>`
        }
        $select.html(opt)

        /////////////////////////////////////////////////

        let metals = getFilterWithCount(json_data, 'Metal');
        $select = $('#selMetal');
        opt = '';
        for (let m of metals) {
            opt += `<option value="${m.value}" data-subtext="(${m.count})">${m.value}</option>`
        }
        $select.html(opt)

        /////////////////////////////////////////////////

        let findRegions = getFilterWithCount(json_data, 'Find Region');
        $select = $('#selFindRegion');
        opt = '';
        for (let fr of findRegions) {
            opt += `<option value="${fr.value}" data-subtext="(${fr.count})">${fr.value}</option>`
        }
        $select.html(opt)

        /////////////////////////////////////////////////

        let authority = getFilterWithCount(json_data, 'Authority');
        $select = $('#selAuthority');
        opt = '';
        for (let a of authority) {
            opt += `<option value="${a.value}" data-subtext="(${a.count})">${a.value}</option>`
        }
        $select.html(opt)

        //////////////////////////////////////////////
        //if (Object.keys(selectedDropdowns).length === 0)
        $('.selectpicker').selectpicker("refresh");
        setSelectedValues();
    }

    function setSelectedValues() {
        if (Object.keys(selectedDropdowns).length > 0) {
            for (let p in selectedDropdowns) {
                if (p !== '') {
                    // $.each(selectedDropdowns[p], function (i, e) {
                    //     $(`#${p}`).val(e)
                    //     var optionByValue =  $(`#${p} option[value='${e}']`);
                    //     $(optionByValue).prop("selected", true);
                    // });

                    $(`#${p}`).val(selectedDropdowns[p])
                    $(`#${p}`).selectpicker("refresh");
                }
            }

            //// 
            $('#btnRefineSearch').removeClass('d-none')
        }
        else {
            $('#btnRefineSearch').addClass('d-none')
        }
    }

    function getFilterWithCount(data, fieldName) {
        // Create a frequency map
        const frequencyMap = {};
        $.each(data, function (index, item) {
            const field = item[fieldName] || 'Unknown';
            if (field !== 'Unknown')
                frequencyMap[field] = (frequencyMap[field] || 0) + 1;
        });

        // Convert frequency map to an array of objects
        let filters = $.map(frequencyMap, function (count, value) {
            return {
                value: value,
                count: count
            };
        });

        filters.sort(function (a, b) {
            return b.count - a.count;
        });

        return filters
    }

    $('.selectpicker').on('hidden.bs.select', function () {
        let selects = $('.selectpicker')
        let objFiltered = {}
        let $currentSelect = $(this);
        let isSelected = false;
        $.each(selects, function (index, select) {
            if ($(select).val().length > 0) {
                let field = $(select).attr('field')
                let values = $(select).val()

                objFiltered[field] = values
                isSelected = true;
            }
        });

        if (isSelected) {
            $table.bootstrapTable('refreshOptions', {
                filterOptions: {
                    filterAlgorithm: 'and'
                }
            })

            selectedDropdowns[$currentSelect.attr('id')] = [...new Set($currentSelect.val())]
        }
        else {
            selectedDropdowns = {}
        }

        $table.bootstrapTable('filterBy', objFiltered)
        loadFilters();
    });

    // $('#btnRefineSearch').click(function () {
    //     loadMap();
    // })

    $('.date').on('keyup', function () {
        let isEmpty = true;
        $.each($('.date'), function (i, ele) {
            if ($(ele).val() !== '')
                isEmpty = false;
        })
        if (isEmpty === false) {
            $('#btnRefineSearch').removeClass('d-none')
        }
        else {
            $('#btnRefineSearch').addClass('d-none')
        }
    })

    const myOffcanvas = document.getElementById('offcanvasWithBothOptions')
    myOffcanvas.addEventListener('hidden.bs.offcanvas', event => {
        loadMap();
    })
})

