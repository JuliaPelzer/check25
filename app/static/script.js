// add task on enter
let input = document.getElementById("taskInput");
input.addEventListener("keypress", function (event) {
  if (event.key === "Enter") {
    addTask();
  }
});

// add click handlers to buttons of tasks
let taskList = document.getElementById("taskList");
let btns = taskList.getElementsByTagName("button");
for (let i = 0; i < btns.length; i++) {
  btns[i].onclick = removeTask;
}

// add click handlers to checkboxes of tasks
let checkboxes = taskList.getElementsByTagName("input");
for (let i = 0; i < checkboxes.length; i++) {
  checkboxes[i].onclick = modifyDone;
}


async function addTask() {
  const taskInput = document.getElementById("taskInput");
  const taskList = document.getElementById("taskList");

  const taskText = taskInput.value;
  if (taskText.trim() !== "") {
    let response = await fetch("/add?done=false&text=" + taskText, {
      method: "POST",
    });
    let body = await response.json();

    const taskItem = document.createElement("li");
    taskItem.className = "py-2 flex items-center justify-between";
    taskItem.id = body["id"];

    const taskWrapper = document.createElement("div");
    taskItem.appendChild(taskWrapper);

    const checkbox = document.createElement("input");
    checkbox.onclick = modifyDone;
    checkbox.type = "checkbox";
    checkbox.className = "mr-2";
    taskWrapper.appendChild(checkbox);

    const taskTextElement = document.createElement("span");
    taskTextElement.textContent = taskText;
    taskWrapper.appendChild(taskTextElement);

    const deleteButton = document.createElement("button");
    deleteButton.className = "px-2 py-1 rounded";
    deleteButton.onclick = removeTask;

    const icon = document.createElement("i");
    icon.className = "fa-solid fa-trash";
    deleteButton.appendChild(icon);
    taskItem.appendChild(deleteButton);

    taskList.appendChild(taskItem);
    taskInput.value = "";
  }
}

function removeTask(param) {
  let id = this.parentNode === undefined ? param.parentNode.id : this.parentNode.id;
  let obj = this.parentNode ? this.parentNode : param.parentNode;
  fetch("/delete?id=" + id, { method: "DELETE" });
  obj.remove();
}

function modifyDone(param) {
  let id = this.parentNode.parentNode.id;
  let done = this.checked;
  fetch("/modify?id=" + id + "&done=" + done, {method: "MODIFY"})
}