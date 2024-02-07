
d3.csv('data/Candid-Trimmed.csv').then(function (data) {
    data.forEach(function (d) {
        delete d['']; // Removes unneeded columns that may or may not exist
        delete d['Unnamed: 0'];
        delete d['Unnamed: 0.1'];
    });


    const params = new URLSearchParams(window.location.search)
    const ein = params.get('ein');

    console.log(ein)
    const this_org_data = data.find(org => org.ein === ein)
    console.log(this_org_data)

    const more_or_less = this_org_data.average_female_salary > this_org_data.average_male_salary ? "more" : "less"
    const payGapText = `Women are paid <span class='percentHighlight'>${Math.round(Math.abs(this_org_data.pay_gap))}%</span> ${more_or_less} than men at ${this_org_data.org_name}`

    document.querySelector("#companyName").insertAdjacentHTML('beforeend', this_org_data.org_name);
    document.querySelector("#payGapText").innerHTML = payGapText;
    createGauge(this_org_data.total_score)


    const leadership_score = parseInt(this_org_data['Trustees']) + parseInt(this_org_data['Highest Compensated']) + parseInt(this_org_data['Officers'])
    let leadership_bar = `
    <div class="cat-score-container">
      <div class="rectangle" style="width: ${leadership_score / 30 * 100}%"></div>
    </div>
    `
    document.querySelector("#leadership").insertAdjacentHTML('beforeend', leadership_bar);

    const pay_score = parseInt(this_org_data['Pay Gap']) + parseInt(this_org_data['Average Salary']) + parseInt(this_org_data['CEO Pay Ratio'])
    let pay_bar = `
    <div class="cat-score-container">
      <div class="rectangle" style="width: ${pay_score / 20 * 100}%"></div>
    </div>
    `
    document.querySelector("#pay").insertAdjacentHTML('beforeend', pay_bar);


    const diversity_score = parseInt(this_org_data['Candid Reporting']) + parseInt(this_org_data['Diversity Reporting'])

    let diversity_bar = `
    <div class="cat-score-container">
      <div class="rectangle" style="width: ${diversity_score / 10 * 100}%"></div>
    </div>
    `
    document.querySelector("#diversity").insertAdjacentHTML('beforeend', diversity_bar);

    const policy_score = 0
    let policy_bar = `
    <div class="cat-score-container">
      <div class="rectangle" style="width: ${policy_score}%"></div>
    </div>
    `
    document.querySelector("#policy").insertAdjacentHTML('beforeend', policy_bar);

    createBoardGenderCompositionViz(this_org_data)
    createPayGraph(this_org_data)
    createCircleComparison(this_org_data)
    createDiversityGraph(this_org_data)



}).catch(function (error) {
    console.error('Error loading data: ', error);
});

function scoreToAngle(score) {
    // Assuming score is in range 0-100
    const maxScore = 100;
    const angleRange = Math.PI;
    return (score / maxScore) * angleRange - angleRange / 2;
}

function createGauge(score) {
    const n = 5;
    const colors = ["#FF0000", "#FFA500", "#FFFF00", "#008000", "#0000FF"];
    const sectionAngle = Math.PI / n;

    const width = 500;
    const height = 475;
    const margin = { top: 20, right: 20, bottom: 20, left: 0 };

    const needleLength = 200;
    const needlePivotX = width / 2;
    const needlePivotY = height * 0.75;

    const svg = d3
        .select(`.circleGraphSpot`)
        .append("svg")
        .attr("width", width)
        .attr("height", height)
        .append("g")
        .attr("transform", `translate(${margin.left}, ${margin.top})`);

    // Create an arc for each section
    for (let i = 0; i < n; i++) {
        const startAngle = -Math.PI / 2 + i * sectionAngle;
        const endAngle = startAngle + sectionAngle;

        const sectionArc = d3
            .arc()
            .innerRadius(120)
            .outerRadius(180)
            .startAngle(startAngle)
            .endAngle(endAngle)
            .cornerRadius(4);

        svg
            .append("path")
            .attr("d", sectionArc)
            .attr("transform", `translate(${width / 2}, ${height * 0.75})`)
            .style("fill", colors[i % colors.length]);
    }
    // Base of needle
    svg
        .append("circle")
        .attr("cx", needlePivotX)
        .attr("cy", needlePivotY)
        .attr("r", 2.5)
        .style("fill", "black")
        .style("stroke", "none");

    const needleAngle = scoreToAngle(score) * (180 / Math.PI);

    svg
        .append("line")
        .attr("x1", needlePivotX)
        .attr("y1", needlePivotY)
        .attr("x2", needlePivotX)
        .attr("y2", needlePivotY - needleLength)
        .style("stroke", "black")
        .style("stroke-width", 2)
        .attr(
            "transform",
            `rotate(${needleAngle}, ${needlePivotX}, ${needlePivotY})`
        );

    const score_color = colors[Math.floor(score / 20)];
    svg
        .append("text")
        .attr("x", needlePivotX)
        .attr("y", needlePivotY - 70)
        .text(`${score}/100`)
        .attr("text-anchor", "middle")
        .style("font-size", "1.5rem")
        .style("font-family", "Poppins")
        .style("fill", "#5e5b5b");
}

function createBoardGenderCompositionViz(orgData) {
    d3.select('#leadershipGraph svg').remove();

    const width = 450, height = 450;
    const radius = Math.min(width, height) / 2 - 40;
    const svg = d3.select("#leadershipGraph")
        .append("svg")
        .attr("width", width)
        .attr("height", height)
        .append("g")
        .attr("transform", "translate(" + width / 2 + "," + height / 2 + ")");

    const color = d3.scaleOrdinal()
        .domain(["Female", "Male", "Non-Binary", "Decline to State", "Unknown"])
        .range(["#3fd796", "#0192f5", "green", "purple", "grey"]);

    const pie = d3.pie()
        .value(d => d[1]);

    const data_ready = pie(Object.entries({
        "Female": orgData.female_board,
        "Male": orgData.male_board,
        "Non-Binary": orgData.non_binary_board,
        "Decline to State": orgData.gender_decline_to_state_board,
        "Unknown": orgData.gender_unknown_board
    }));

    const total = Object.entries({
        "Female": orgData.female_board,
        "Male": orgData.male_board,
        "Non-Binary": orgData.non_binary_board,
        "Decline to State": orgData.gender_decline_to_state_board,
        "Unknown": orgData.gender_unknown_board
    }).reduce((acc, curr) => acc + (+curr[1]), 0);

    console.log(total)

    const arc = d3.arc()
        .innerRadius(0)
        .outerRadius(radius);

    svg
        .selectAll('slices')
        .data(data_ready)
        .enter()
        .append('path')
        .attr('d', arc)
        .attr('fill', d => color(d.data[0]))
        .style("opacity", 0.7)
        .on("mouseover", function (event, d) {
            const categoryCount = d.data[1];
            const categoryPercentage = ((categoryCount / total) * 100).toFixed(2);

            d3.select("#tooltip")
                .style("display", "block")
                .html(d.data[0] + ": " + categoryPercentage + "% (" + categoryCount + " members)")
                .style("left", (event.pageX + 10) + "px")
                .style("top", (event.pageY - 20) + "px");
        })
        .on("mouseout", function () {
            d3.select("#tooltip").style("display", "none");
        });

    // Add a title
    svg.append("text")
        .attr("x", 0)
        .attr("y", -height / 2 + 15)
        .text("Board Composition by Gender")
        .attr("text-anchor", "middle")
        .style("font-size", "20px")
        .style("font-weight", "bold")
        .style("font-family","Raleway");

    // Add a label for the total number of board members
    svg.append("text")
        .attr("x", 0)
        .attr("y", -height / 2 + 35)
        .text("Total Board Members: " + total)
        .attr("text-anchor", "middle")
        .style("font-size", "14px")
        .style("font-weight", "bold")
        .style("font-family","Raleway");
}

function formatNumberAbbreviated(num) {
    if (num >= 1000) {
        const abbreviatedNum = num / 1000;

        const formatter = new Intl.NumberFormat('en-US', {
            maximumFractionDigits: 0,
            minimumFractionDigits: 0
        });

        return formatter.format(abbreviatedNum) + 'K';
    } else {
        const formatter = new Intl.NumberFormat('en-US');
        return formatter.format(num);
    }
}

function createPayGraph(orgData) {

    d3.select('#highestPaidGraph svg').remove();

    console.log(orgData);

    const data = [
        { gender: 'Male', compensation: orgData.average_male_salary, color: "#d69e62" },
        { gender: 'Female', compensation: orgData.average_female_salary, color: "#b862fd" }
    ];



    console.log(data)
    // https://observablehq.com/@d3/horizontal-bar-chart/2
    const barHeight = 25;
    const marginTop = 30;
    const marginRight = 0;
    const marginBottom = 85;
    const marginLeft = 30;
    const width = 750;
    const height = Math.ceil(4 * barHeight) + marginTop + marginBottom + 50;



    const x = d3.scaleLinear()
        .domain([0, d3.max(data, d => d.compensation)])
        .range([marginLeft, width - marginRight]);

    const y = d3.scaleBand()
        .domain(["Male", "Female"])
        .range([marginTop, height - marginBottom])

    const svg = d3.select("#highestPaidGraph")
        .append("svg")
        .attr("width", width)
        .attr("height", height)
        .attr("viewBox", [0, 0, width, height])
        .attr("style", "max-width: 100%; height: auto; font: 10px sans-serif;");

    svg.append("g")
        .selectAll()
        .data(data)
        .join("rect")
        .attr("x", x(0))
        .attr("y", (d) => y(d.gender))
        .attr("fill", (d) => d.gender == "Female" ? "#b862fd" : "#d69e62")
        .attr("width", (d) => x(d.compensation) - x(0))
        .attr("height", y.bandwidth());

    svg.append("g")
        .attr("transform", `translate(0,${marginTop})`)

    svg.append("g")
        .attr("transform", `translate(${marginLeft},0)`)

    svg.append("g")
        .attr("fill", "black")
        .attr("text-anchor", "end")
        .selectAll()
        .data(data)
        .join("text")
        .attr("x", (d) => x(d.compensation))
        .attr("y", (d) => y(d.gender) + y.bandwidth() / 2)
        .attr("dy", "0.35em")
        .attr("dx", -4)
        .attr("font-size", "1.3rem")
        .text((d) => formatNumberAbbreviated(d.compensation))
        .attr("font-family", "Poppins")

    svg.append("text")
        .attr("x", marginLeft)
        .attr("y", marginTop / 2)
        .attr("text-anchor", "right")
        .attr("font-size", "1.2rem")
        .attr("font-family", "Raleway")
        .text("Highest Paid Employee Avg Compensation");


    const legendSpacing = 5;
    const legendRectSize = 18;
    const legendX = marginLeft - 15;
    const legendY = height - marginBottom / 2;

    svg.append("rect")
        .attr("x", legendX - 5)
        .attr("y", legendY - legendRectSize)
        .attr("width", 120)
        .attr("height", legendRectSize * 3 + legendSpacing)
        .attr("fill", "grey")
        .style("opacity", 0.3)
        .attr("rx", 10)
        .attr("ry", 10);

    const legend = svg.selectAll(".legend")
        .data(data)
        .enter().append("g")
        .attr("class", "legend")
        .attr("transform", (d, i) => `translate(${legendX},${legendY + i * (legendRectSize + legendSpacing)})`);

    legend.append("circle")
        .attr("r", legendRectSize / 2)
        .attr("cx", legendRectSize / 2)
        .attr("fill", d => d.color);

    legend.append("text")
        .attr("x", legendRectSize + legendSpacing)
        .attr("y", legendRectSize / 3.5)
        .attr("font-size", ".75rem")
        .text(d => d.gender);

}

function createCircleComparison(orgData) {

    d3.select('#payGraph svg').remove();

    highest_salary = Math.round(+orgData.highest_salary);
    avg_employee_comp = Math.round(+orgData.avg_employee_comp);

    const width = 550, height = 550;
    const svg = d3.select("#payGraph").append("svg").attr("width", width).attr("height", height);
    const scaleFactor = 0.0001;

    const hierarchyData = {
        "name": "Salaries",
        "children": [
            { "name": "Highest Salary", "value": highest_salary * scaleFactor, "color": "#ff883a" },
            { "name": "Average Employee Salary", "value": avg_employee_comp * scaleFactor, "color": "#3fd796" }
        ]
    };

    const pack = d3.pack().size([width, height]).padding(5);
    const root = d3.hierarchy(hierarchyData).sum(d => d.value);
    const nodes = pack(root).descendants();

    const node = svg.selectAll(".node")
        .data(nodes.filter(d => d.depth === 1))
        .join("g")
        .attr("class", "node")
        .attr("transform", d => `translate(${d.x}, ${d.y})`)


    node.append("circle")
        .attr("r", d => d.r)
        .style("fill", d => d.data.color)
        .style("stroke-width", 4)

    node.append("text")
        .style("text-anchor", "middle")
        .style("dominant-baseline", "central")
        .text(d => formatNumberAbbreviated(d.data.value / scaleFactor))
        .attr("fill", "black")
        .attr("font-family", "Poppins")
        .attr("font-size", "1.2rem")


    svg.append("text")
        .attr("x", width / 2)
        .attr("y", 20)
        .text("CEO vs Average Employee")
        .attr("text-anchor", "middle")
        .style("font-size", "24px")
        .style("font-family", "Raleway")
        .style("fill", "black");

    const drag = d3.drag()
        .on("start", dragstarted)
        .on("drag", dragged)
        .on("end", dragended);

    node.call(drag)

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
                })
                .attr("transform", function (d) {
                    return `translate(${Math.max(d.r, Math.min(width - d.r, d.x))}, ${Math.max(d.r, Math.min(height - d.r, d.y))})`
                })

        });



    function dragstarted(event, d) {
        if (!event.active) simulation.alphaTarget(.03).restart();
        d.fx = d.x;
        d.fy = d.y;
    }

    function dragged(event, d) {
        d.fx = event.x;
        d.fy = event.y;
        d3.select(this)
            .attr("transform", `translate(${event.x}, ${event.y})`);
        d.x = event.x;
        d.y = event.y;
    }

    function dragended(event, d) {
        if (!event.active) simulation.alphaTarget(.03);
        d.fx = null;
        d.fy = null;
    }

}

function createDiversityGraph(orgData) {

    d3.select('#diversityGraph svg').remove()


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

    const margin = { top: 100, right: 30, bottom: 150, left: 70 },
        width = d3.select('body').node().getBoundingClientRect().width * 0.75 - margin.left - margin.right,
        height = 500 - margin.top - margin.bottom;


    const svg = d3.select("#diversityGraph")
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
        .attr("fill", "#3fd796")
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