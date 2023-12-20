function closeAllLists(elmnt) {
    var x = document.getElementsByClassName("autocomplete-items");
    for (var i = 0; i < x.length; i++) {
        if (elmnt != x[i] && elmnt != document.getElementById('searchBox')) {
            x[i].parentNode.removeChild(x[i]);
        }
    }
}

function addHighlightedNameMatches(data, inputValue, parentElement) {
    data.forEach(org => {
        let orgName = org.org_name;
        if (orgName.toUpperCase().includes(inputValue.toUpperCase())) {
            let matchIndex = orgName.toUpperCase().indexOf(inputValue.toUpperCase());
            let b = document.createElement("DIV");
            b.innerHTML = `${orgName.substr(0, matchIndex)}<strong>${orgName.substr(matchIndex, inputValue.length)}</strong>${orgName.substr(matchIndex + inputValue.length)}`;
            b.innerHTML += "<input type='hidden' value='" + orgName + "'>";
            b.addEventListener("click", function (e) {
                document.getElementById('searchBox').value = this.getElementsByTagName("input")[0].value;
                createBarChartForOrg(data, this.getElementsByTagName("input")[0].value);
                createCircleComparison(data, this.getElementsByTagName("input")[0].value);
                createPayGapViz(data, this.getElementsByTagName("input")[0].value);
                closeAllLists();
            });
            parentElement.appendChild(b);
        }
    });
}


d3.csv('data/Candid-Top.csv').then(function (data) {
    data.forEach(function (d) {
        delete d[""]; // Removes the index of the dataset which is meaningless
    });



    // Search box autocomplete
    document.getElementById('searchBox').addEventListener('input', function (e) {
        let a, b, i, val = this.value;
        closeAllLists();
        if (!val) { return false; }
        a = document.createElement("DIV");
        a.setAttribute("id", this.id + "autocomplete-list");
        a.setAttribute("class", "autocomplete-items");
        this.parentNode.appendChild(a);

        addHighlightedNameMatches(data, val, a);
    });




    // Close all autocomplete lists when someone clicks in the document
    document.addEventListener("click", function (e) {
        closeAllLists(e.target);
    });

}).catch(function (error) {
    console.error('Error loading data: ', error);
})


function createBarChartForOrg(data, org_name) {

    d3.select('#d3viz svg').remove()


    const orgData = data.find(d => d.org_name === org_name);


    const ethnicityData = [
        { ethnicity: "Asian", count: +orgData.asian_staff },
        { ethnicity: "Black", count: +orgData.black_staff },
        { ethnicity: "Hispanic", count: +orgData.hispanic_staff },
        { ethnicity: "Middle Eastern", count: +orgData.middle_eastern_staff },
        { ethnicity: "Native American", count: +orgData.native_american_staff },
        { ethnicity: "Pacific Islander", count: +orgData.pacific_islander_staff },
        { ethnicity: "White", count: +orgData.white_staff },
        { ethnicity: "Multi-Racial", count: +orgData.multi_racial_staff },
        { ethnicity: "Other", count: +orgData.other_ethnicity_staff },
        { ethnicity: "Decline to state", count: +orgData.race_decline_to_state_staff },
        { ethnicity: "Unknown", count: +orgData.race_unknown_staff },
    ];

    const margin = { top: 60, right: 30, bottom: 100, left: 60 },
        width = d3.select('body').node().getBoundingClientRect().width * 0.5 - margin.left - margin.right,
        height = 400 - margin.top - margin.bottom;


    // Append the svg object to the div 'd3viz'
    const svg = d3.select("#d3viz")
        .append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", `translate(${margin.left},${margin.top})`);

    // X axis
    const x = d3.scaleBand()
        .range([0, width])
        .domain(ethnicityData.map(d => d.ethnicity))
        .padding(0.2);

    svg.append("g")
        .attr("transform", `translate(0, ${height})`)
        .call(d3.axisBottom(x))
        .selectAll("text")
        .attr("transform", "translate(-10,0) rotate(-45)")
        .style("text-anchor", "end")
        .style("font-size", "0.8rem");

    // Add Y axis
    const y = d3.scaleLinear()
        .domain([0, d3.max(ethnicityData, d => d.count)])
        .range([height, 0]);

    svg.append("g")
        .call(d3.axisLeft(y));

    // Bars
    svg.selectAll("mybar")
        .data(ethnicityData)
        .enter()
        .append("rect")
        .attr("x", d => x(d.ethnicity))
        .attr("y", d => y(d.count))
        .attr("width", x.bandwidth())
        .attr("height", d => height - y(d.count))
        .attr("fill", "#30173f");


    svg.append("text")
        .attr("x", (width / 2))
        .attr("y", (margin.top / 2) - 60)
        .attr("text-anchor", "middle")
        .style("font-size", "20px")
        .style("text-decoration", "underline")
        .text("Staff Ethnicity Distribution");

    svg.append("text")
        .attr("x", (width / 2))
        .attr("y", (margin.top / 2) - 40)
        .attr("text-anchor", "middle")
        .style("font-size", "16px")
        .text(org_name);

    // X axis label
    svg.append("text")
        .attr("text-anchor", "end")
        .attr("x", width / 2 + margin.left)
        .attr("y", height + margin.top + 20)
        .text("Ethnicity")

    // Y axis label
    svg.append("text")
        .attr("text-anchor", "end")
        .attr("transform", "rotate(-90)")
        .attr("y", -margin.left + 20)
        .attr("x", -margin.top)
        .text("Staff Count");


    const tooltip = d3.select("body").append("div")
        .attr("class", "tooltip")
        .style("opacity", 0)
        .style("position", "absolute")
        .style("text-align", "center")
        .style("width", "80px")
        .style("height", "14px")
        .style("padding", "2px")
        .style("font", "12px sans-serif")
        .style("background", "lightsteelblue")
        .style("border", "0px")
        .style("border-radius", "8px")

    svg.selectAll(".bar")
        .data(ethnicityData)
        .enter()
        .append("rect")
        .attr("x", d => x(d.ethnicity))
        .attr("y", d => y(d.count))
        .attr("width", x.bandwidth())
        .attr("height", d => height - y(d.count))
        .attr("fill", "#30173f")
        .on("mouseover", function (event, d) {
            tooltip.transition()
                .duration(200)
                .style("opacity", .9);
            tooltip.html(d.count)  // The text displayed in the tooltip (d is the datapoint for the bar, so count is the height)
                .style("left", (event.pageX) + "px")
                .style("top", (event.pageY - 28) + "px");
        })
        .on("mousemove", function (event) {
            tooltip.style("left", (event.pageX) + "px")
                .style("top", (event.pageY - 28) + "px");
        })
        .on("mouseout", function (d) {
            tooltip.transition()
                .duration(500)
                .style("opacity", 0);
        });


}

function createCircleComparison(data, org_name) {

    d3.select('#d3viz2 svg').remove();
    const orgData = data.find(d => d.org_name === org_name);
    console.log(orgData);
    highest_salary = Math.round(+orgData.highest_salary);
    avg_employee_comp = Math.round(+orgData.avg_employee_comp);

    const width = 450, height = 450;
    const svg = d3.select("#d3viz2").append("svg").attr("width", width).attr("height", height);
    const scaleFactor = 0.0001;

    const hierarchyData = {
        "name": "Salaries",
        "children": [
            { "name": "Highest Salary", "value": highest_salary * scaleFactor },
            { "name": "Average Employee Salary", "value": avg_employee_comp * scaleFactor }
        ]
    };

    console.log(hierarchyData);

    const pack = d3.pack().size([width, height]).padding(5);
    const root = d3.hierarchy(hierarchyData).sum(d => d.value);
    const nodes = pack(root).descendants();

    const node = svg.selectAll("circle")
        .data(nodes.filter(d => d.depth === 1))
        .join("circle")
        .attr("r", d => d.r)
        .attr("cx", d => d.x)
        .attr("cy", d => d.y)
        .style("fill", "lightblue")
        .style("fill-opacity", 0.3)
        .attr("stroke", "#b3a2c8")
        .style("stroke-width", 4)
        .call(d3.drag()
            .on("start", dragstarted)
            .on("drag", dragged)
            .on("end", dragended));


    svg.append("text")
        .attr("x", width / 2)
        .attr("y", 20)
        .text("Salary Comparison")
        .attr("text-anchor", "middle")
        .style("font-size", "24px")
        .style("fill", "black");

    node.on("mouseover", function (event, d) {
        d3.select("#tooltip")
            .style("display", "block")
            .html(d.data.name + "<br>$" + Intl.NumberFormat().format(Math.round(d.data.value / scaleFactor)))
            .style("left", (event.pageX + 10) + "px")
            .style("top", (event.pageY - 20) + "px");
    })
        .on("mouseout", function () {
            d3.select("#tooltip").style("display", "none");
        });



    const simulation = d3.forceSimulation()
        .force("center", d3.forceCenter().x(width / 2).y(height / 2))

    simulation
        .nodes(nodes)
        .on("tick", () => {
            node
                .attr("cx", function (d) {
                    return d.x = Math.max(d.r, Math.min(width - d.r, d.x));
                })
                .attr("cy", function (d) {
                    return d.y = Math.max(d.r, Math.min(height - d.r, d.y));
                });
        });



    function dragstarted(event, d) {
        if (!event.active) simulation.alphaTarget(.03).restart();
        d.fx = d.x;
        d.fy = d.y;
    }

    function dragged(event, d) {
        d.fx = event.x;
        d.fy = event.y;
    }

    function dragended(event, d) {
        if (!event.active) simulation.alphaTarget(.03);
        d.fx = null;
        d.fy = null;
    }

}

function createPayGapViz(data, org_name) {
    d3.select('#payGapViz svg').remove();
    data = data.find(d => d.org_name === org_name);
    const width = 500, height = 400;
    const margin = { top: 50, right: 30, bottom: 50, left: 60 };
    const svg = d3.select("#payGapViz")
        .append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    svg.append("text")
        .attr("x", width / 2)
        .attr("y", -margin.top / 2)
        .text("Pay Gap in Highest Compensated")
        .attr("text-anchor", "middle")
        .style("font-size", "20px")
        .style("font-weight", "bold")
        .style("fill", "#333");


    const xScale = d3.scaleBand()
        .range([0, width])
        .domain(["Female", "Male"])
        .padding(0.4);
    const yScale = d3.scaleLinear()
        .range([height, 0])
        .domain([0, Math.max(data.average_female_salary, data.average_male_salary) * 1.1]);

    svg.append("g")
        .selectAll("rect")
        .data([data.average_female_salary, data.average_male_salary])
        .enter()
        .append("rect")
        .attr("x", (d, i) => xScale(i === 0 ? "Female" : "Male"))
        .attr("y", d => yScale(d))
        .attr("width", xScale.bandwidth())
        .attr("height", d => height - yScale(d))
        .attr("fill", (d, i) => i === 0 ? "pink" : "blue");

    // Add labels for average salary
    svg.append("g")
        .selectAll("text")
        .data([data.average_female_salary, data.average_male_salary])
        .enter()
        .append("text")
        .text(d => `$${Intl.NumberFormat().format(Math.round(d))}`)
        .attr("x", (d, i) => xScale(i === 0 ? "Female" : "Male") + xScale.bandwidth() / 2)
        .attr("y", d => yScale(d) - 5)
        .attr("text-anchor", "middle")
        .style("fill", "black");

    // Add Pay Gap Label
    svg.append("text")
        .text(`Pay Gap: ${(+data.pay_gap).toFixed(1)}%`)
        .attr("x", width / 2)
        .attr("y", 20)
        .attr("text-anchor", "middle")
        .style("font-size", "14px")
        .style("fill", d => data.pay_gap > 0 ? "blue" : "orange");

    // Add percentage labels
    const percentages = [data.percent_female, data.percent_male];
    svg.append("g")
        .selectAll("text")
        .data(percentages)
        .enter()
        .append("text")
        .text(d => `${Math.round(d)}% pop.`)
        .attr("x", (d, i) => xScale(i === 0 ? "Female" : "Male") + xScale.bandwidth() / 2)
        .attr("y", height - 10)
        .attr("text-anchor", "middle")
        .attr("fill", "grey");

    // X-axis
    svg.append("g")
        .attr("transform", `translate(0,${height})`)
        .call(d3.axisBottom(xScale));

    // Y-axis
    svg.append("g")
        .call(d3.axisLeft(yScale));
}