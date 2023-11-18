async function make_interactive() {
  let postalcode = new URLSearchParams(window.location.search).get("postalcode");

  let response = await fetch("/craftsmen?postalcode=" + postalcode);
  
  let data = await response.json();
  let craftsmen = data["craftsmen"];

  let provider_list = document.getElementById("provider_list");
  const template = document.querySelector("#provider");
  
  for (let i = 0; i < craftsmen.length && i < 20; i++) {
    const clone = template.content.cloneNode(true);
    let name = clone.querySelector("h3");
    console.log(name)
    name.textContent = craftsmen[i]["name"];
    provider_list.appendChild(clone);
  }
}

make_interactive()