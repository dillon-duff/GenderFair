// Import the functions you need from the SDKs you need
import { initializeApp } from 'https://www.gstatic.com/firebasejs/10.9.0/firebase-app.js'
import { getFirestore, doc, getDoc, collection, query, where, getDocs } from "https://cdnjs.cloudflare.com/ajax/libs/firebase/10.9.0/firebase-firestore.js";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
    apiKey: "AIzaSyAgMFt2ritERn0jQATbdhuqIp1ZDUNQ-oI",
    authDomain: "gender-fair-82d21.firebaseapp.com",
    databaseURL: "https://gender-fair-82d21-default-rtdb.firebaseio.com",
    projectId: "gender-fair-82d21",
    storageBucket: "gender-fair-82d21.appspot.com",
    messagingSenderId: "607866022549",
    appId: "1:607866022549:web:0bd2d5eb81d1447c72c99c",
    measurementId: "G-KHE8JG192F"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);

// Initialize Firestore
const db = getFirestore(app);

async function fetchDocumentByEIN(ein) {
    const nonprofitsRef = collection(db, "non-for-profits");
    const queryRef = query(nonprofitsRef,
        where("ein", "==", ein),
    );
    const querySnapshot = await getDocs(queryRef);
    querySnapshot = querySnapshot.docs.map(doc => ({
        id: doc.id,
        ...doc.data()
    }))

    if (querySnapshot.length > 0) {
        return querySnapshot[0];
    } else {
        return null;
    }
}



async function fetchDocumentsByRankRange(startRank, endRank) {
    const nonprofitsRef = collection(db, "non-for-profits");
    const queryRef = query(nonprofitsRef,
        where("rank", ">=", startRank),
        where("rank", "<", endRank)
    );
    const querySnapshot = await getDocs(queryRef);

    return querySnapshot;
}

// fetchDocumentByID("001Dj1Z9GqSMOnHSYsyE").catch(console.error);
fetchDocumentsByRankRange(0, 49).catch(console.error);


let data_candid;
let data_990;

let curr_rank = 0;
let currentPage = 1;
const recordsPerPage = 50;
let filteredData = [];
let currentData = [];
let allData = [];
let lastPage = currentPage;

function scrollSmoothTo(elementId) {
    var element = document.getElementById(elementId);
    element.scrollIntoView({
        block: 'start',
        behavior: 'smooth'
    });
}
window.scrollSmoothTo = scrollSmoothTo;

async function changePage(increment) {
    const numPages = Math.ceil(data_candid.length / recordsPerPage);
    lastPage = currentPage;
    currentPage += increment;

    if (currentPage < 1) currentPage = 1;
    if (currentPage > numPages) currentPage = numPages;

    curr_rank = currentPage * 50 - 50;

    document.getElementById('currentPage').textContent = currentPage;

    const startIdx = (currentPage - 1) * recordsPerPage;
    const endIdx = startIdx + recordsPerPage;
    console.log(startIdx, endIdx)
    // currentData = allData.slice(startIdx, endIdx);
    currentData = await fetchDocumentsByRankRange(startIdx, endIdx);
    currentData = currentData.docs.map(doc => ({
        id: doc.id,
        ...doc.data()
    }))

    // filteredData = [];

    renderData();
}
window.changePage = changePage;


function renderData() {
    const container = document.querySelector('.data-rows');
    container.innerHTML = ``;

    let toRender = [];

    if (filteredData.length > 0) {
        toRender = filteredData;
    } else {
        toRender = currentData;
    }

    console.log(toRender)

    toRender.forEach(function (org) {
        curr_rank++;
        let score = org.final_score;

        const orgHtml = `
            <div class="org-row" data-ein="${org.ein}">
                <div class="input-rank">#${curr_rank}</div>
                <div class="input-org">${org.name}</div>
                <div class="score-container">
                    <div class="rectangle" style="width: ${score}%"></div>
                </div>
                <div class="score">${score}</div>
            </div>
        `;

        container.insertAdjacentHTML('beforeend', orgHtml);

    });
    document.querySelectorAll('.org-row').forEach(row => {
        row.addEventListener('click', function () {
            const ein = this.getAttribute('data-ein');
            const currentUrl = new URL(window.location.href);
            const targetUrl = new URL(`breakdown.html?ein=${ein}`, currentUrl.origin);
            window.location.href = targetUrl.href;
        });
    });
}

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

    allData = data_candid;

    changePage(0);

}).catch(function (error) {
    console.error('Error loading data: ', error);
});

document.getElementById('searchBox').addEventListener('input', function () {
    const query = this.value.toLowerCase();
    if (!query) {
        filteredData = [];
        currentPage = 1;
        changePage(0);
        return;
    }
    filteredData = allData.filter(d => d.org_name.toLowerCase().includes(query));
    if (filteredData.length <= 0) {
        this.classList.add('no-results');
        this.disabled = true;

        setTimeout(() => {
            this.disabled = false;
            this.focus();
        }, 500);
    } else {
        this.classList.remove('no-results');
        this.disabled = false;
    }
    currentPage = 1;
    changePage(0);
});