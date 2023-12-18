
function createGauge(containerId, score) {
  const n = 5;
  const colors = ["#FF0000", "#FFA500", "#FFFF00", "#008000", "#0000FF"];
  const sectionAngle = Math.PI / n;

  const width = 200;
  const height = 100;
  const margin = { top: 20, right: 20, bottom: 20, left: 20 };

  const needleLength = 70;
  const needlePivotX = width / 2;
  const needlePivotY = height;

  const svg = d3.select(`#${containerId}`)
    .append("svg")
    .attr("width", width)
    .attr("height", height)
    .append("g")
    .attr("transform", `translate(${margin.left}, ${margin.top})`);


  // Create an arc for each section
  for (let i = 0; i < n; i++) {
    const startAngle = -Math.PI / 2 + i * sectionAngle;
    const endAngle = startAngle + sectionAngle;

    const sectionArc = d3.arc()
      .innerRadius(40)
      .outerRadius(60)
      .startAngle(startAngle)
      .endAngle(endAngle);

    svg.append("path")
      .attr("d", sectionArc)
      .attr("transform", `translate(${width / 2}, ${height})`)
      .style("fill", colors[i % colors.length]);
  }


  const needleAngle = scoreToAngle(score) * (180 / Math.PI);

  svg.append("line")
    .attr("x1", needlePivotX)
    .attr("y1", needlePivotY)
    .attr("x2", needlePivotX)
    .attr("y2", needlePivotY - needleLength)
    .style("stroke", "black")
    .style("stroke-width", 2)
    .attr("transform", `rotate(${needleAngle}, ${needlePivotX}, ${needlePivotY})`);

}


function scoreToAngle(score) {
  // Assuming score is in range 0-100
  const maxScore = 100;
  const angleRange = Math.PI;
  return (score / maxScore) * angleRange - (angleRange / 2);
}
function updateGauge(containerId, newScore) {
  const newAngle = scoreToAngle(newScore);
  d3.select(`#${containerId} line`)
    .transition()
    .duration(1000)
    .attr("transform", `translate(${width / 2}, ${height}) rotate(${newAngle})`);
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
  ['B'].forEach(company => {
    for (let i = 1; i <= 3; i++) {
      const score = getRandomScore();
      console.log("company", company, "score", score, "i", i);

      // Replace this
      // createGauge(`gauge${company}${i}`, score);
    }
  });
});