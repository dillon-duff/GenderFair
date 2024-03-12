let data_candid;
let data_990;

// var lastScrollTop;
// navbar = document.getElementById('navbar');
// window.addEventListener('scroll',function(){
// var scrollTop = window.pageYOffset || document.documentElement.scrollTop;
// if(scrollTop > lastScrollTop){
//     navbar.style.top='-80px';
// }
// else{
//     navbar.style.top='0';
// }
// lastScrollTop = scrollTop;
// });

Promise.all([
    d3.csv('data/Candid-Trimmed.csv'),
    d3.csv('data/990-Top.csv')
]).then(function (files) {
    files[0].forEach(function (d) {
        delete d['']; // Removes unneeded columns that may or may not exist
        delete d['Unnamed: 0'];
        delete d['Unnamed: 0.1'];
    });
    console.log("Candid Data:");
    console.log(files[0]);
    data_candid = files[0];

    files[1].forEach(function (d) {
        delete d['']; // Removes unneeded columns that may or may not exist
        delete d['Unnamed: 0'];
        delete d['Unnamed: 0.1'];
    });
    console.log("990 Data:");
    console.log(files[1]);
    data_990 = files[1];

    let curr_rank = 0;

    data_candid.forEach(function (org) {
        curr_rank++;
        let score = org.total_score;

        const orgHtml = `
            <div class="org-row" data-ein="${org.ein}">
                <div class="input-rank">#${curr_rank}</div>
                <div class="input-org">${org.org_name}</div>
                <div class="score-container">
                    <div class="rectangle" style="width: ${score}%"></div>
                </div>
                <div class="score">${score}</div>
            </div>
        `;

        document.querySelector(".scoreboard").insertAdjacentHTML('beforeend', orgHtml);

    });

    document.querySelectorAll('.org-row').forEach(row => {
        row.addEventListener('click', function () {
            const ein = this.getAttribute('data-ein');
            window.location.href = `${window.location.href}breakdown.html?ein=${ein}`;
        });
    });



    const orgHtml = `
    <div class="org-row">
        <div class="input-rank">#1</div>
        <div class="input-org" id="specificOrganization">org A</div>
        <div class="score-container">
          
          <div class="rectangle"></div>
        </div>
        <div class="score">95</div>

      </div>
      `



}).catch(function (error) {
    console.error('Error loading data: ', error);
});

