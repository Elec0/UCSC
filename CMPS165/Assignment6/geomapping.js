/*jslint vars: true, plusplus: true, devel: true, nomen: true, indent: 4, maxerr: 50 */
/*global d3*/

//Define Margin
var margin = {left: 80, right: 80, top: 50, bottom: 50 }, 
    width = 960 - margin.left -margin.right,
    height = 500 - margin.top - margin.bottom,
    scaleWidth=width + margin.left + margin.right,
    scaleHeight=50;

//Define SVG
var svg = d3.select("body").append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
    .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")")

var scale = d3.select("body").append("svg")
    .attr("width", scaleWidth)
    .attr("height", scaleHeight);

var gradient1 = scale.append("defs")
    .append("linearGradient")
    .attr("id", "gradient1")
    .attr("x1", "0%")
    .attr("y1", "0%")
    .attr("x2", "100%")
    .attr("y2", "0%")
    .attr("spreadMethod", "pad");
var gradient2 = scale.append("defs")
    .append("linearGradient")
    .attr("id", "gradient2")
    .attr("x1", "0%")
    .attr("y1", "0%")
    .attr("x2", "100%")
    .attr("y2", "0%")
    .attr("spreadMethod", "pad");
var gradient3 = scale.append("defs")
    .append("linearGradient")
    .attr("id", "gradient3")
    .attr("x1", "0%")
    .attr("y1", "0%")
    .attr("x2", "100%")
    .attr("y2", "0%")
    .attr("spreadMethod", "pad");



var scaleX = d3.scaleLinear()
    .domain([-25,0]) // Give appropriate range in the scale
    .range([0,width]);

var scaleY = d3.scaleLinear()
    .domain([50, 70]) // Give appropriate range in the scale
    .range([height, 0]);

var color0 = "#FFFFFF", color1 = "#AAFFAA", color10 = "#5555FF", color200 = "#FF0000";

var color = d3.scaleLinear()
    .domain([0,1,10,200])
    .range([d3.rgb(color0), d3.rgb(color1), d3.rgb(color10), d3.rgb(color200)]);

var projection = d3.geoMercator()
    .scale(3500)
    .center([-19, 65])
    .translate([width / 2, height / 2]);

var path = d3.geoPath()
    .projection(projection);

var popArea = null;
d3.csv("IcelandArea.csv", function(data) {
    data.forEach(function(d) { 
        d.Population = +d.Population;
        d.Area = +d.Area;
    });
    popArea = data;
});

d3.json("iceland-2-simpl-2.json", function(data) {
    var features = data.features;
    
    /*features.forEach(function (d) {
        if(getPopArea(d.properties.NAME_2) == null) {
            console.log(d.properties.NAME_2);
        }
    });*/
    
    scaleX.domain([d3.min(features, function(d) { if(d.geometry == null) { return Infinity;  } else { return d.geometry.coordinates[0][0][0]; } }),
                   d3.max(features, function(d) { if(d.geometry == null) { return -Infinity; } else { return d.geometry.coordinates[0][0][0]; } })]);
    scaleY.domain([d3.min(features, function(d) { if(d.geometry == null) { return -Infinity; } else { return d.geometry.coordinates[0][0][1]; } }), 
                   d3.max(features, function(d) { if(d.geometry == null) { return Infinity;  } else { return d.geometry.coordinates[0][0][1]; } })]);
    
    // Draw each province as a path
    // Taken from http://bl.ocks.org/almccon/fe445f1d6b177fd0946800a48aa59c71
    svg.selectAll('path')
        .data(features)
        .enter().append('path')
        .attr('d', path)
        .attr("fill", areaFill)
        .attr("stroke","black")
        .attr("stroke-width", 1)
        .on('mouseover', mouseover)
        .on('mouseout', mouseout);
});

// ***** Scale Start ***** \\
// 0 - 1 scale
gradient1.append("stop")
    .attr("offset", "0%")
    .attr("stop-color", color0)
    .attr("stop-opacity", 1);

gradient1.append("stop")
    .attr("offset", "100%")
    .attr("stop-color", color1)
    .attr("stop-opacity", 1);

// 1 - 10 scale
gradient2.append("stop")
    .attr("offset", "0%")
    .attr("stop-color", color1)
    .attr("stop-opacity", 1);

gradient2.append("stop")
    .attr("offset", "100%")
    .attr("stop-color", color10)
    .attr("stop-opacity", 1);

// 10 - 200 scale
gradient3.append("stop")
    .attr("offset", "0%")
    .attr("stop-color", color10)
    .attr("stop-opacity", 1);

gradient3.append("stop")
    .attr("offset", "100%")
    .attr("stop-color", color200)
    .attr("stop-opacity", 1);

// Actually render the scale
scale.append("text")
    .attr("x", 0)
    .attr("y", 10)
    .attr("style", "font-weight:bold")
    .text("Population density scale (People / square kilometer)");

scale.append("rect")
    .attr("x", 0)
    .attr("y", scaleHeight/4)
    .attr("fill", "url(#gradient1)")
    .attr("width", scaleWidth/10)
    .attr("height", scaleHeight/2);

scale.append("rect")
    .attr("x", scaleWidth/10)
    .attr("y", scaleHeight/4)
    .attr("fill", "url(#gradient2)")
    .attr("width", scaleWidth/3)
    .attr("height", scaleHeight/2);

scale.append("rect")
    .attr("x", (scaleWidth/10+scaleWidth/3))
    .attr("y", scaleHeight/4)
    .attr("fill", "url(#gradient3)")
    .attr("width", (scaleWidth-(scaleWidth/10+scaleWidth/3)))
    .attr("height", scaleHeight/2);


scale.append("text")
    .attr("x", 0)
    .attr("y", scaleHeight)
    .text("0");
scale.append("text")
    .attr("x", scaleWidth/10)
    .attr("y", scaleHeight)
    .text("1");

scale.append("text")
    .attr("x", scaleWidth/3+scaleWidth/10)
    .attr("y", scaleHeight)
    .text("10");

scale.append("text")
    .attr("x", scaleWidth-25)
    .attr("y", scaleHeight)
    .text("200");

// ***** Scale End ***** \\

// Checks if there is a partial match of up to n characters. Returns true if there is, false if not
function partialCompare(str1, str2, n) {
    // If the string doesn't even go up to our n, return false right off the bat
    if(str1.legnth < n || str2.length < n)
        return false;
    
    for(var i = 0; i < n; ++i) {
        // If, at any point, they don't match, fail.
        if(str1[i] !== str2[i])
            return false;
    }
    return true;
}

function areaFill(d) {
    var pA = getPopArea(d.properties.NAME_2);
    if(pA != null) {
        // If area isn't null we can calc population density
        if(pA.Area != null) {
            var density = pA.Population / pA.Area
            //console.log(density);
            return color(density);
        }
        else {
            // If it is null we can only display population
            console.log(pA.Population);
        }
    }
    else {
        // We have absolutely no data on this area at all
        return "white";
    }
}

function getPopArea(mun) {
    for(var i = 0; i < popArea.length; ++i) {
        if(partialCompare(popArea[i].Municipality, mun, mun.length/2))
            return popArea[i];   
    }
    return null;
}

function mouseover(d) {
//    d3.select(this).style('fill', 'orange');
    console.log(getPopArea(d.properties.NAME_2));
}

function mouseout(d) {
//    d3.select(this).style('fill', 'transparent');
}