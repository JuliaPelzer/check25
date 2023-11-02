let input = document.getElementById("taskInput");
input.addEventListener("keypress", function(event) {
  if (event.key === "Enter") {
    addTask();
  }
})

async function addTask() {
  const taskInput = document.getElementById("taskInput");
  const taskList = document.getElementById("taskList");

  const taskText = taskInput.value;
  if (taskText.trim() !== "") {
    let response = await fetch(
      "/add?done=false&text=" + taskText,
      { method: "POST" },
    );
    let body = await response.json();

    const taskItem = document.createElement("li");
    taskItem.className = "py-2 flex items-center justify-between";

    const taskWrapper = document.createElement("div");
    taskItem.appendChild(taskWrapper);

    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.className = "mr-2";
    taskWrapper.appendChild(checkbox);

    const taskTextElement = document.createElement("span");
    taskTextElement.textContent = taskText;
    taskWrapper.appendChild(taskTextElement);

    const deleteButton = document.createElement("button");
    deleteButton.id = body["id"];
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
  let id = this.id ? this.id : param.id;
  let obj = this.id ? this : param;
  fetch("/delete?id=" + id, { method: "DELETE" });
  obj.parentNode.remove();
}
