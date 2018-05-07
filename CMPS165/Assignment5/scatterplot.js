/*jslint vars: true, plusplus: true, devel: true, nomen: true, indent: 4, maxerr: 50 */
/*global d3*/

//Define Margin
var margin = {left: 80, right: 80, top: 50, bottom: 50 }, 
    width = 960 - margin.left -margin.right,
    height = 500 - margin.top - margin.bottom;

//Define Color
var colors = d3.scaleOrdinal(d3.schemeCategory20);

//Define SVG
var svg = d3.select("body").append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
    .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")")
    .attr("id", "mainG")
    .append("g")
    .attr("id", "dotRender");

var svgAxis = d3.select("#mainG");

//Define Scales
// X scale is GDP
var xScale = d3.scaleLinear()
    .domain([0,16]) //Need to redefine this after loading the data
    .range([0, width]);

// Y scale is ecc (million BTUs per person)
var yScale = d3.scaleLinear()
    .domain([0,450]) //Need to redfine this after loading the data
    .range([height, 0]);


var zoom = d3.zoom()
    .scaleExtent([1, 40])
    //.translateExtent([[-100, -100], [width + 90, height + 100]])
    .on("zoom", zoomed);

//Define Axis
var xAxis = d3.axisBottom().scale(xScale).tickPadding(2);
var yAxis = d3.axisLeft().scale(yScale).tickPadding(2);


d3.select("svg").call(zoom);

//Get Data
// Define domain for xScale and yScale
d3.csv("scatterdata.csv", function(error, data) {
    data.forEach(function(d) {
        // Convert into numbers
        d.gdp = +d.gdp;
        d.population = +d.population;
        d.ecc = +d.ecc;
        d.ec = +d.ec;
    });

    // Redefine domain for x and y axes
    xScale.domain([0, d3.max(data, function(d) { return d.gdp; })]);
    yScale.domain([0, d3.max(data, function(d) { return d.ecc; })]);

    //Draw Scatterplot
    svg.selectAll(".dot")
        .data(data)
        .enter().append("circle")
        .attr("class", "dot")
        .attr("r", function(d) { return Math.sqrt(d.ecc); }) // Scaling needs to be changed somehow
        .attr("cx", function(d) {return xScale(d.gdp);})
        .attr("cy", function(d) {return yScale(d.ecc);})
        .style("fill", function (d) { return colors(d.country); })
        .on("mouseover", handleMouseOver)
        .on("mouseout", handleMouseOut);
    //Add .on("mouseover", .....
    //Add Tooltip.html with transition and style
    //Then Add .on("mouseout", ....

    //Scale Changes as we Zoom
    // Call the function d3.behavior.zoom to Add zoom

    //Draw Country Names
    svg.selectAll(".text")
        .data(data)
        .enter().append("text")
        .attr("class","text")
        .style("text-anchor", "start")
        .attr("x", function(d) {return xScale(d.gdp);})
        .attr("y", function(d) {return yScale(d.ecc);})
        .style("fill", "black")
        .text(function (d) {return d.country; });

});


function handleMouseOver(d) {
    var tooltip = svg.append("g")
        .attr("id", "tooltip");
    
    var left = xScale(d.gdp)+5;
    var top = yScale(d.ecc)+5;
    
    tooltip.append("rect")
        .attr("x", left)
        .attr("y", top)
        .attr("rx", 25)
        .attr("ry", 25)
        .attr("width", 170)
        .attr("height", 90);
   
    // Country Name
    tooltip.append("text")
        .attr("x", left+=10)
        .attr("y", top+=20)
        .text(d.country);
    
    // Population
    tooltip.append("text")
        .attr("x", left)
        .attr("y", top+=15)
        .text("Population: " + d.population + " million");
    
    // GDP
    tooltip.append("text")
        .attr("x", left)
        .attr("y", top+=15)
        .text("GDP: $" + d.gdp + " trillion");
    
    // EPC
    tooltip.append("text")
        .attr("x", left)
        .attr("y", top+=15)
        .text("EPC: " + d.ecc + " million BTUs");
    
    // Total
    tooltip.append("text")
        .attr("x", left)
        .attr("y", top+=15)
        .text("Total: " + d.ec + " trillion BTUs");
}

function handleMouseOut() {
    svg.select("#tooltip").remove();
}

//x-axis
var sXAxis = svgAxis.append("g")
    .attr("class", "x axis")
    .attr("transform", "translate(0," + height + ")")
    .call(xAxis);
//    .text("GDP (in Trillion US Dollars) in 2010");


//Y-axis
var sYAxis = svgAxis.append("g")
    .attr("class", "y axis")
    .call(yAxis);
//    .text(")");


// The graph label
svgAxis.append("text")
    .attr("text-anchor", "middle")  // this makes it easy to centre the text as the transform is applied to the anchor
    .attr("transform", "translate(-35, "+(height/2)+")rotate(-90)")  // text is drawn off the screen top left, move down and out and rotate
    .text("Energy Consumption per Capita (in Million BTUs per person")
    .attr("font-size", "12px");

// The x axis label
svgAxis.append("text")
    .attr("text-anchor", "middle")  // this makes it easy to centre the text as the transform is applied to the anchor
    .attr("transform", "translate(" + (width/2) + ", " + (height+30) + ")")  // text is drawn off the screen top left, move down and out and rotate
    .text("GDP (in Trillion US Dollars) in 2010")
    .attr("font-size", "12px");

 // draw legend colored rectangles
svgAxis.append("rect")
    .attr("x", width-250)
    .attr("y", height-190)
    .attr("width", 180)
    .attr("height", 70)
    .attr("fill", "lightgrey")
    .style("stroke-size", "1px");

svgAxis.append("circle")
    .attr("r", Math.sqrt(1))
    .attr("cx", width-100)
    .attr("cy", height-175)
    .style("fill", "green");

svgAxis.append("circle")
    .attr("r", Math.sqrt(10))
    .attr("cx", width-100)
    .attr("cy", height-160)
    .style("fill", "green");

svgAxis.append("circle")
    .attr("r", Math.sqrt(100))
    .attr("cx", width-100)
    .attr("cy", height-135)
    .style("fill", "green");

svgAxis.append("text")
    .attr("class", "label")
    .attr("x", width-150)
    .attr("y", height-172)
    .style("text-anchor", "end")
    .text(" 1 Million BTUs");

svgAxis.append("text")
    .attr("class", "label")
    .attr("x", width-150)
    .attr("y", height-155)
    .style("text-anchor", "end")
    .text(" 10 Million BTUs");

svgAxis.append("text")
    .attr("class", "label")
    .attr("x", width-150)
    .attr("y", height-135)
    .style("text-anchor", "end")
    .text(" 100 Million BTUs");


// https://bl.ocks.org/mbostock/db6b4335bf1662b413e7968910104f0f
function zoomed() {
    d3.select("#dotRender").attr("transform", d3.event.transform);
    
    sXAxis.call(xAxis.scale(d3.event.transform.rescaleX(xScale)));
    sYAxis.call(yAxis.scale(d3.event.transform.rescaleY(yScale)));
}