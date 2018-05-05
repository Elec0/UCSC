/* ----------------------------------------------------------------------------
File: BarGraphSample.js
Contructs the Bar Graph using D3
80 characters perline, avoid tabs. Indet at 4 spaces. See google style guide on
JavaScript if needed.
-----------------------------------------------------------------------------*/

// Search "D3 Margin Convention" on Google to understand margins.
// Add comments here in your own words to explain the margins below
// The margins are defined here with whatever we want to call them, and they're
// then used automatically, and we don't have to think about them anymore
// which is important for ranges and such (we can do [0,width], for example)
var margin = {top: 10, right: 40, bottom: 150, left: 50},
    width = 760 - margin.left - margin.right,
    height = 500 - margin.top - margin.bottom;
    

// Define SVG. "g" means group SVG elements together. 
// Add comments here in your own words to explain this segment of code
var svg = d3.select("body").append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
    .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

/* --------------------------------------------------------------------
SCALE and AXIS are two different methods of D3. See D3 API Refrence and 
look up SVG AXIS and SCALES. See D3 API Refrence to understand the 
difference between Ordinal vs Linear scale.
----------------------------------------------------------------------*/ 

// Define X and Y SCALE.
// Add comments in your own words to explain the code below
// xScale is the mapping function for the country name to their x location
// The padding is the amount of space between each bar.
var xScale = d3.scaleBand().rangeRound([0, width]).padding(0.1);

// yScale a function mapping the y values to their height
var yScale = d3.scaleLinear().range([height, 0]);

// Define X and Y AXIS
// Define tick marks on the y-axis as shown on the output with an interval of 5 and $ sign
var xAxis = d3.axisBottom(xScale);
var yAxis = d3.axisLeft(yScale).ticks(5).tickFormat( function(d) { return "$" + d; });

/* --------------------------------------------------------------------
To understand how to import data. See D3 API refrence on CSV. Understand
the difference between .csv, .tsv and .json files. To import a .tsv or
.json file use d3.tsv() or d3.json(), respectively.
----------------------------------------------------------------------*/ 

// data.csv contains the country name(key) and its GDP(value)
// d.key and d.value are very important commands
// You must provide comments here to demonstrate your understanding of these commands
d3.csv("GDP2016TrillionUSDollars.csv", function(error, data) {
    data.forEach(function(d) {
        // We had to actually use the data we were given
        // Since it's csv we get the type of data with the labels and put them in 
        // the key/value
        d.key = d.country;
        d.value = +d.gdp;
    });

    
    // Return X and Y SCALES (domain). See Chapter 7:Scales (Scott M.) 
    // We set the ranges earlier, so set the domains now
    // Range = y, domain = x
    xScale.domain(data.map(function(d){ return d.key; }));    
    yScale.domain([0, d3.max(data, function(d) { return d.value; })]);
    
    // Creating rectangular bars to represent the data. 
    // Add comments to explain the code below
    svg.selectAll("rect")
        .data(data) // Bind the data so we can use it, which also makes this code run for as much data as we have
        .enter()
        .append("g") // We need a group of items because there's going to be rect + text
        .append("rect") // Add the rects we need for the data
        .transition().duration(1000)
        .delay( function(d,i) {return i * 50;})
        .attr("x", function(d) { return xScale(d.key); }) // X location, use the xScale function
        .attr("y", function(d) { return yScale(d.value); }) // Y location, use the yScale function
        .attr("width", xScale.bandwidth())
        .attr("height", function(d) { return height - yScale(d.value); })
        .attr("style", function(d) { // create increasing to decreasing shade of blue as shown on the output
            var colorValStart = 100; // Start with a darker shade of blue and add as we go up
            var colorVal = colorValStart + Math.floor(xScale(d.key)/6);
            // We divide by 6 to make sure we don't overflow from 255
            return "fill: #0000" + colorVal.toString(16) +";" // Do the hex math as we go up in x
        });
    
    // Idea taken from https://stackoverflow.com/questions/19182775/d3-data-skipping-the-first-row-of-data 
    // Selecting all g.rect elements to make sure we are getting the right gs.
    svg.selectAll("g.rect")
        .data(data)
        .enter()
        .append("text")
        .transition().duration(1000) // Copy the transition from the bars
        .delay( function(d,i) {return i * 50;})
        .text(function(d) {
            // The actual text we're outputting is the gdp
            return d.gdp;
        })
        .attr("text-anchor", "middle")
        .attr("x", function(d) {
            // Position the numbers in the middle of the bars
            return xScale(d.country) + 20;
        })
        .attr("y", function(d) {
            // Position the numbers in the middle of the bars
            return yScale(d.value) + 12;
        })
        .attr("font-family", "sans-serif")
        .attr("font-size", "11px")
        .attr("fill", "white");


    // Draw xAxis and position the label at -60 degrees as shown on the output 
    svg.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + height + ")")
        .call(xAxis)
        .selectAll("text")
        .attr("transform", "rotate(-60)")
        .attr("dx", "-.8em")
        .attr("dy", ".25em")
        .style("text-anchor", "end")
        .attr("font-size", "10px");


    // Draw yAxis and position the label
    svg.append("g")
        .attr("class", "y axis")
        .attr("transform", "translate(0, 0)")
        .call(yAxis);

    // The graph label
    svg.append("text")
        .attr("text-anchor", "middle")  // this makes it easy to centre the text as the transform is applied to the anchor
        .attr("transform", "translate(-40, "+(height/2)+")rotate(-90)")  // text is drawn off the screen top left, move down and out and rotate
        .text("Trillions of US Dollars ($)")
        .attr("font-size", "12px")
        .attr("font-weight", "bold");
});

        
    
