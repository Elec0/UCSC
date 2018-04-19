/*jslint vars: true, plusplus: true, devel: true, nomen: true, indent: 4, maxerr: 50 */
/*global d3*/

var margin = {top: 10, right: 70, bottom: 150, left: 50},
    width = 800 - margin.left - margin.right,
    height = 500 - margin.top - margin.bottom;
    

var svg = d3.select(".graph").append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
    .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

var timeFormat = d3.timeFormat("%Y");
var timeParse = d3.timeParse("%Y");

var xScale = d3.scaleTime().rangeRound([0, width]);
var yScale = d3.scaleLinear().range([height, 0]);
var zScale = d3.scaleOrdinal(d3.schemeCategory10);

var xAxis = d3.axisBottom(xScale).ticks(11).tickFormat( function(d) { return timeFormat(d); });
var yAxis = d3.axisLeft(yScale);


// Checkboxes from https://bl.ocks.org/johnnygizmo/3d593d3bf631e102a2dbee64f62d9de4

var line = d3.line()
    .curve(d3.curveBasis)
    .x(function(d, i) {var yr = "20" + (i > 9 ? i : "0" + i); return xScale(timeParse(yr)); })
    .y(function(d) { return yScale(d); });

// Load the data from the csv file into the program.
// I'm going for the superbonus points, so I'm not changing the data at all.
d3.csv("BRICSdata.csv", function(error, data) {
    data.forEach(function(d) {
        // We're making the data better formatted here, since we're not changing the .csv file
        // It's organized as (Country, year0-year10)        
        d.value = [];
            
        // Loop over each key,value in the dictionary
        for (var key in d) 
        {
            // check if the property/key is defined in the object itself, not in parent
            if (d.hasOwnProperty(key)) {
                // Prevent loading the country data into the array
                if(key != "Country" && key != "value")
                {
                    d.value.push(+d[key]);
                    delete d[key];
                }
            }
        }        
    });

    
    // Set the X scale as a range of actual dates
    xScale.domain([timeParse("2000"), timeParse("2010")]);
    // This fun monstrosity gets the max from a dictionary of arrays
    yScale.domain([0, d3.max(data, function(d) { return (d3.max(d.value, function(e) { return e; })); })]);
    

    var city = svg.selectAll(".city")
        .data(data)
        .enter()
        .append("g")
        .attr("class", "city");
    
    city.append("path")
        .attr("class", "line")
        .attr("d", function(d) { return line(d.value); })
        .style("stroke", function(d, i) { return zScale(i); })
        // Everything below here is for the animation
        .attr("stroke-dasharray", function() {
            var totalLength = this.getTotalLength();
            return totalLength + " " + totalLength;
        })
        .attr("stroke-dashoffset", function() {
            var totalLength = this.getTotalLength();
            return totalLength;
        })
        .transition()
            .duration(function() { return 1000 + Math.random() * 4000;})
            .ease(d3.easeLinear)
            .attr("stroke-dashoffset", 0);
    
    // The line lables
    city.append("text")
        .datum(function(d, i) { return {country: d.Country, id: i, value: d.value[d.value.length - 1]}; })
        .attr("transform", function(d) { return "translate(" + xScale(timeParse("2010")) + "," + yScale(d.value) + ")"; })
        .attr("x", 3)
        .attr("dy", "0.35em")
        .style("font", "10px sans-serif")
        .text(function(d) { return d.country; });

    
    /* ***************** */
    /* ** Axis Drawing   */
    /* ***************** */
    
    // Draw xAxis and position the label at -60 degrees as shown on the output 
    svg.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0, " + height +")")
        .call(xAxis);
    

    // Draw yAxis and position the label
    svg.append("g")
        .attr("class", "y axis")
        .attr("transform", "translate(0, 0)")
        .call(yAxis);

    /* ***************** */
    /* ** Gridlines   ** */
    /* ***************** */
    // Taken from https://bl.ocks.org/d3noob/c506ac45617cf9ed39337f99f8511218
    // gridlines in x axis function
    function make_x_gridlines() {		
        return d3.axisBottom(xScale)
            .ticks(5)
    }
    // gridlines in y axis function
    function make_y_gridlines() {		
        return d3.axisLeft(yScale)
            .ticks(5)
    }
    // add the X gridlines
    svg.append("g")			
        .attr("class", "grid")
        .attr("transform", "translate(0," + height + ")")
        .call(make_x_gridlines()
        .tickSize(-height)
        .tickFormat(""));

    // add the Y gridlines
    svg.append("g")			
        .attr("class", "grid")
        .call(make_y_gridlines()
        .tickSize(-width)
        .tickFormat(""));
    
    /* ***************** */
    /* ** Main Labels ** */
    /* ***************** */
    
    // The graph label
    svg.append("text")
        .attr("text-anchor", "middle")  // this makes it easy to centre the text as the transform is applied to the anchor
        .attr("transform", "translate(-35, "+(height/2)+")rotate(-90)")  // text is drawn off the screen top left, move down and out and rotate
        .text("Million BTUs Per Person")
        .attr("font-size", "17px");
    
    // The x axis label
    svg.append("text")
        .attr("text-anchor", "middle")  // this makes it easy to centre the text as the transform is applied to the anchor
        .attr("transform", "translate(" + (width+25) + ", " + (height+20) + ")")  // text is drawn off the screen top left, move down and out and rotate
        .text("Year")
        .attr("font-size", "12px");
});

        
    