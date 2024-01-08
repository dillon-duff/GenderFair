
function createGauge(containerId, score) {
  const n = 5;
  const colors = ["#FF0000", "#FFA500", "#FFFF00", "#008000", "#0000FF"];
  const sectionAngle = Math.PI / n;

  const width = 200;
  const height = 100;
  const margin = { top: 20, right: 20, bottom: 20, left: 20 };

  const needleLength = 70;
  const needlePivotX = width / 2;
  const needlePivotY = height * 0.75;

  const svg = d3.select(`#${containerId}`)
    .append("svg")
    .attr("width", width)
    .attr("height", height)
    .append("g")
    .attr("transform", `translate(${margin.left}, ${margin.top})`);

  // Label for minimum value
  svg.append("text")
    .attr("x", width / 2 - 60)
    .attr("y", height)
    .text("0")
    .style("font-size", "10px")
    .attr("text-anchor", "middle");



  // Create an arc for each section
  for (let i = 0; i < n; i++) {
    const startAngle = -Math.PI / 2 + i * sectionAngle;
    const endAngle = startAngle + sectionAngle;

    const sectionArc = d3.arc()
      .innerRadius(40)
      .outerRadius(60)
      .startAngle(startAngle)
      .endAngle(endAngle)
      .cornerRadius(4);

    svg.append("path")
      .attr("d", sectionArc)
      .attr("transform", `translate(${width / 2}, ${height * 0.75})`)
      .style("fill", colors[i % colors.length]);
  }
  // Base of needle
  svg.append("circle")
  .attr("cx", needlePivotX)
  .attr("cy", needlePivotY)
  .attr("r", 2.5)
  .style("fill", "black")
  .style("stroke", "none");


  const needleAngle = scoreToAngle(score) * (180 / Math.PI);

  svg.append("line")
    .attr("x1", needlePivotX)
    .attr("y1", needlePivotY)
    .attr("x2", needlePivotX)
    .attr("y2", needlePivotY - needleLength)
    .style("stroke", "black")
    .style("stroke-width", 2)
    .attr("transform", `rotate(${needleAngle}, ${needlePivotX}, ${needlePivotY})`);

  const score_color = colors[Math.floor(score / 20)];
  svg.append("text")
    .attr("x", needlePivotX)
    .attr("y", needlePivotY - 70)
    .text(score)
    .attr("text-anchor", "middle")
    .style("font-size", "16px")
    .style("font-weight", "bold")
    .style("fill", "#222");

}

function createCircularProgress(containerId, score) {
  const width = 100, height = 100, radius = 40;
  const svg = d3.select(`#${containerId}`)
    .append("svg")
    .attr("width", width)
    .attr("height", height)
    .append("g")
    .attr("transform", `translate(${width / 2}, ${height / 2})`);

  const backgroundArc = d3.arc()
    .innerRadius(radius - 10)
    .outerRadius(radius)
    .startAngle(0)
    .endAngle(Math.PI * 2);

  svg.append("path")
    .attr("d", backgroundArc)
    .style("fill", "#ddd");

  const percentScale = d3.scaleLinear()
    .domain([0, 100])
    .range([0, Math.PI * 2]);

  const percentArc = d3.arc()
    .innerRadius(radius - 10)
    .outerRadius(radius)
    .startAngle(0)
    .endAngle(percentScale(score));

  svg.append("path")
    .attr("d", percentArc)
    .style("fill", "orange");

  svg.append("text")
    .attr("text-anchor", "middle")
    .attr("alignment-baseline", "middle")
    .style("font-size", "20px")
    .text(score);
}

function createHorizontalBar(containerId, score) {
  const width = 200, height = 50;
  const svg = d3.select(`#${containerId}`)
    .append("svg")
    .attr("width", width)
    .attr("height", height);

  svg.append("rect")
    .attr("width", width)
    .attr("height", height)
    .style("fill", "#ddd");

  svg.append("rect")
    .attr("width", (score / 100) * width)
    .attr("height", height)
    .style("fill", "orange");

  svg.append("text")
    .attr("x", (score / 100) * width - 5)
    .attr("y", height / 2)
    .attr("text-anchor", "end")
    .attr("alignment-baseline", "middle")
    .style("font-size", "14px")
    .text(score);
}

function createScatterPlot(containerId, score) {
  const width = 200, height = 100;
  const padding = 20;

  const svg = d3.select(`#${containerId}`)
    .append("svg")
    .attr("width", width)
    .attr("height", height);

  // X scale
  const xScale = d3.scaleLinear()
    .domain([0, 100])
    .range([padding, width - padding]);

  // Base line
  svg.append("line")
    .attr("x1", padding)
    .attr("y1", height / 2)
    .attr("x2", width - padding)
    .attr("y2", height / 2)
    .style("stroke", "#ddd")
    .style("stroke-width", 2);

  svg.append("circle")
    .attr("cx", xScale(score))
    .attr("cy", height / 2)
    .attr("r", 5)
    .style("fill", "red");

  svg.append("text")
    .attr("x", xScale(score))
    .attr("y", height / 2 + 20)
    .text(score)
    .style("font-size", "16px")
    .attr("text-anchor", "start");
}


function scoreToAngle(score) {
  // Assuming score is in range 0-100
  const maxScore = 100;
  const angleRange = Math.PI;
  return (score / maxScore) * angleRange - (angleRange / 2);
}



function getRandomScore() {
  return Math.floor(Math.random() * 101); // Random score between 0 and 100
}
document.addEventListener('DOMContentLoaded', function () {
  // Initialize gauges for each company with random scores
  ['A'].forEach(company => {
    for (let i = 1; i <= 3; i++) {
      const score = getRandomScore();

      console.log("company", company, "score", score, "i", i);
      createGauge(`gauge${company}${i}`, score);
    }
  });
  // ['B'].forEach(company => {
  //   for (let i = 1; i <= 3; i++) {
  //     const score = getRandomScore();
  //     console.log("company", company, "score", score, "i", i);

  //     createCircularProgress(`gauge${company}${i}`, score);
  //   }
  // });
  // ['C'].forEach(company => {
  //   for (let i = 1; i <= 3; i++) {
  //     const score = getRandomScore();
  //     console.log("company", company, "score", score, "i", i);

  //     createHorizontalBar(`gauge${company}${i}`, score);
  //   }
  // });
  // ['D'].forEach(company => {
  //   for (let i = 1; i <= 3; i++) {
  //     const score = getRandomScore();
  //     console.log("company", company, "score", score, "i", i);
  //     createScatterPlot(`gauge${company}${i}`, score);
  //   }
  // });

});