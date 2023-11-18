let displayed = 0;
let craftsmen;

async function make_interactive() {
  let postalcode = new URLSearchParams(window.location.search).get("postalcode");

  let response = await fetch("/craftsmen?postalcode=" + postalcode);

  let data = await response.json();
  craftsmen = data["craftsmen"];

  let numba = document.getElementById("numba");
  numba.textContent = "Yeahy, we found " + craftsmen.length + " craftmen in your area!"
  
  if (craftsmen.length < 20) {
    document.getElementById("more").remove()
  }
  
  show_more()
}

function show_more() {
  let provider_list = document.getElementById("provider_list");
  const template = document.querySelector("#provider");
  
  let limit = displayed + 20;

  for (let i = displayed; i < craftsmen.length && i < limit; i++) {
    const clone = template.content.cloneNode(true);
    let name = clone.querySelector("h3");
    name.textContent = craftsmen[i]["name"];
    provider_list.appendChild(clone);
    displayed = i + 1;
  }

  if (displayed >= craftsmen.length) {
    document.getElementById("more").remove()
  }
}

make_interactive()