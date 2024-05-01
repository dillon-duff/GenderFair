// Import the functions you need from the SDKs you need
import { initializeApp } from 'https://www.gstatic.com/firebasejs/10.9.0/firebase-app.js'
import { getFirestore, doc, getDoc, collection, query, where, getDocs, orderBy, limit, getCountFromServer } from "https://cdnjs.cloudflare.com/ajax/libs/firebase/10.9.0/firebase-firestore.js";
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


function chunkArray(array, chunkSize) {
    const chunks = [];
    for (let i = 0; i < array.length; i += chunkSize) {
        const chunk = array.slice(i, i + chunkSize);
        chunks.push(chunk);
    }
    return chunks;
}

async function fetchDocumentsForEINs(db, name, allEINs, categories) {
    const docsLimit = recordsPerPage;
    const chunkSize = Math.floor(30 / categories.length) // categories.length * chunkSize has to be <= 30 because
    const chunkedEINs = chunkArray(allEINs, chunkSize); // Firestore allows up to 30 items in an 'in' query. Also, this number being too big can make the query too complicated and it will fail
    const documents = [];

    for (const chunk of chunkedEINs) {
        const collectionRef = collection(db, "non-for-profits");
        let queryRef = null;
        if (name.length == 0) {
            queryRef = query(collectionRef, where("category", "in", categories), orderBy('rank'), limit(docsLimit));
        } else if (categories == allCategories) {
            queryRef = query(collectionRef, where("ein", "in", chunk), orderBy('rank'), limit(docsLimit));
        } else {
            queryRef = query(collectionRef, where("ein", "in", chunk), where("category", "in", categories), orderBy('rank'), limit(docsLimit));
        }
        const querySnapshot = await getDocs(queryRef);
        querySnapshot.forEach(doc => {
            documents.push(doc.data());
        });
        // This if statement could go in the forEach statement above to actually limit the search results
        if (documents.length >= docsLimit) {
            break;
        }
    }

    return documents.sort((a, b) => a.rank - b.rank);
}

async function fetchDocumentByNameAndCategories(name, categories) {
    // Currently only gets the top 50 results and there is no way to see the rest.
    // This will become an issue when we try to involve paging when using category filters
    name = name.toLowerCase();
    const response = await fetch('../nameToEINMap.json');
    const nameToEINMap = await response.json();

    let fittingEINs = [];
    if (name.length > 0) {
        for (const orgName in nameToEINMap) {
            if (orgName.toLowerCase().includes(name)) {
                fittingEINs.push(nameToEINMap[orgName]);
            }
        }
    } else {
        fittingEINs = Object.keys(nameToEINMap);
    }

    let querySnapshot = await fetchDocumentsForEINs(db, name, fittingEINs, categories);

    if (querySnapshot.length > 0) {
        return querySnapshot;
    } else {
        return null;
    }
}

async function fetchDocumentsByRankRange(startRank, endRank) {
    const nonprofitsRef = collection(db, "non-for-profits");
    if (startRank == 1) startRank = 0;
    const queryRef = query(nonprofitsRef,
        where("rank", ">", startRank),
        where("rank", "<=", endRank)
    );
    const querySnapshot = await getDocs(queryRef);

    return querySnapshot;
}


const allCategories = ["community needs", "children", "healthcare", "other", "education", "college", "arts", "hospital", "environmental", "stem", "hunger"];

let currentPage = 1;
const recordsPerPage = 50;
let filteredData = [];
let currentData = [];

function scrollSmoothTo(elementId) {
    var element = document.getElementById(elementId);
    element.scrollIntoView({
        block: 'start',
        behavior: 'smooth'
    });
}
window.scrollSmoothTo = scrollSmoothTo;

async function getDocumentCount() {
    const coll = collection(db, "non-for-profits");
    const snapshot = await getCountFromServer(coll);
    return snapshot.data().count
}


async function changePage(increment) {
    const numDocs = await getDocumentCount();
    const numPages = Math.ceil(numDocs / recordsPerPage);
    currentPage += increment;

    if (currentPage < 1) currentPage = 1;
    if (currentPage > numPages) currentPage = numPages;

    document.getElementById('currentPage').textContent = currentPage;

    const startIdx = (currentPage - 1) * recordsPerPage;
    const endIdx = startIdx + recordsPerPage;
    currentData = await fetchDocumentsByRankRange(startIdx, endIdx);
    currentData = currentData.docs.map(doc => ({
        id: doc.id,
        ...doc.data()
    }))

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
        let score = org.final_score;

        const orgHtml = `
            <div class="org-row" data-ein="${org.ein}">
                <div class="input-rank"><h3>#${org.rank}</h3></div>
                <div class="input-org"><h3>${capitalizeWords(org.name)}</h3></div>
                <div class="score-container">
                    <div class="rectangle" style="width: ${score}%"></div>
                </div>
                <div class="score"><h3>${score}</h3></div>
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

async function updateTable() {
    document.body.classList.add('cursor-wait');
    const query = document.getElementById('searchBox').value.toLowerCase();
    let categories = getSelectedCategories();

    if (!query && categories == allCategories) {
        console.log("Default search, returning front page");
        filteredData = [];
        currentPage = 1;
        changePage(0);
        document.body.classList.remove('cursor-wait');
        return;
    }


    filteredData = await fetchDocumentByNameAndCategories(query, categories);


    // Styling for search box when there are no results
    // Needs modified to work
    //
    // filteredData = allData.filter(d => d.org_name.toLowerCase().includes(query));
    // if (filteredData.length <= 0) {
    //     this.classList.add('no-results');
    //     this.disabled = true;

    //     setTimeout(() => {
    //         this.disabled = false;
    //         this.focus();
    //     }, 500);
    // } else {
    //     this.classList.remove('no-results');
    //     this.disabled = false;
    // }

    currentPage = 1;
    changePage(0);
    document.body.classList.remove('cursor-wait');
}

function getSelectedCategories() {
    var checkboxes = document.querySelectorAll('#d_items input[type=checkbox]');

    var selectedItems = Array.from(checkboxes)
        .filter(checkbox => checkbox.checked)
        .map(checkbox => checkbox.value);
    if (selectedItems.length == 0) {
        return allCategories;
    }
    return selectedItems.map(item => item.toLowerCase());
}

function capitalizeWords(sentence) {
    const words = sentence.split(' ');
    for (let i = 0; i < words.length; i++) {
        words[i] = words[i].charAt(0).toUpperCase() + words[i].slice(1).toLowerCase();
    }
    return words.join(' ');
}

document.getElementById('searchbar').addEventListener('submit', async function (event) {
    event.preventDefault();
    updateTable();
});

// document.getElementById('filterIcon').addEventListener('click', function () {
//     var dropdown = document.getElementById('dropdown');
//     dropdown.style.display = dropdown.style.display === 'block' ? 'none' : 'block';
// });

document.getElementById('searchIcon').addEventListener('click', function (event) {
    event.preventDefault();
    updateTable();
});

var checkList = document.getElementById('list1');
var dropdown_items =document.getElementById('d_items');
checkList.getElementsByClassName('dropdown-check-list')[0].onclick = function(evt) {
  if (dropdown_items.classList.contains('item-visible'))
  dropdown_items.classList.remove('item-visible');
  else
  dropdown_items.classList.add('item-visible');
}

changePage(0);