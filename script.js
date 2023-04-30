let search = document.getElementById("search");
let test = document.getElementById("test");

search.addEventListener("click", function () {
    alert("hello");
});

test.addEventListener("click", function getHello() {
    fetch("http://18.116.15.185:8000/")
        .then((response) => response.text())
        .then((data) => {
            document.getElementById("hello").innerHTML = data;
        });
});
