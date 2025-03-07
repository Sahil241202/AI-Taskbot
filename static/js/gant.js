document.addEventListener("DOMContentLoaded", function () {
    const addTaskBtn = document.getElementById("addTaskBtn");
    const modal = document.getElementById("taskModal");
    const closeModal = document.querySelector(".close");
    const saveTaskBtn = document.getElementById("saveTaskBtn");
    const taskList = document.getElementById("taskList");
    const ganttHeader = document.getElementById("ganttHeader");
    const ganttBody = document.getElementById("ganttBody");
    const sidebarTaskList = document.getElementById("sidebarTaskList"); // Sidebar Task List

    // Open task modal
    addTaskBtn.addEventListener("click", () => {
        modal.style.display = "block";
    });

    // Close task modal
    closeModal.addEventListener("click", () => {
        modal.style.display = "none";
    });

    // Save task
    saveTaskBtn.addEventListener("click", async () => {
        const name = document.getElementById("taskName").value;
        const assignee = document.getElementById("taskAssignee").value;
        const priority = document.getElementById("taskPriority").value;
        const deadline = document.getElementById("taskDeadline").value;

        const response = await fetch("/add_task", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ name, assignee, priority, deadline }),
        });

        const data = await response.json();
        addTaskToList(data.task);
        addTaskToSidebar(data.task);
        modal.style.display = "none";
    });

    // Load tasks
    async function loadTasks() {
        const response = await fetch("/get_tasks");
        const tasks = await response.json();
        taskList.innerHTML = ""; // Clear existing tasks
        sidebarTaskList.innerHTML = ""; // Clear sidebar
        tasks.forEach(task => {
            addTaskToList(task);
            addTaskToSidebar(task);
        });
    }

    function addTaskToList(task) {
        const li = document.createElement("li");
        li.textContent = task.name;
        li.classList.add("task");
        li.draggable = true;
        li.dataset.id = task.id;
        
        // Hover effect
        li.style.transition = "0.3s";
        li.addEventListener("mouseover", () => li.style.backgroundColor = "#f0f0f0");
        li.addEventListener("mouseout", () => li.style.backgroundColor = "white");

        // Add Delete Button
        const deleteBtn = document.createElement("button");
        deleteBtn.textContent = "Delete";
        deleteBtn.classList.add("delete-btn");
        deleteBtn.onclick = () => deleteTask(task.id);
        
        li.appendChild(deleteBtn);
        taskList.appendChild(li);
    }

    function addTaskToSidebar(task) {
        const taskItem = document.createElement("div");
        taskItem.classList.add("sidebar-task");
        taskItem.textContent = task.name;
        
        // Hover effect
        taskItem.style.transition = "0.3s";
        taskItem.addEventListener("mouseover", () => taskItem.style.backgroundColor = "#e0e0e0");
        taskItem.addEventListener("mouseout", () => taskItem.style.backgroundColor = "transparent");

        sidebarTaskList.appendChild(taskItem);
    }

    async function deleteTask(taskId) {
        if (confirm("Are you sure you want to delete this task?")) {
            try {
                const response = await fetch(`/delete_task/${taskId}`, {
                    method: "DELETE"
                });

                if (response.ok) {
                    loadTasks(); // Refresh the task list and sidebar
                } else {
                    console.error("Delete failed:", await response.text());
                }
            } catch (error) {
                console.error("Delete error:", error);
            }
        }
    }

    function setupGantt() {
        const days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
        for (let i = 4; i <= 13; i++) {
            const dayDiv = document.createElement("div");
            dayDiv.classList.add("day");
            dayDiv.textContent = `${days[i % 7]} ${i}`;
            dayDiv.dataset.day = i;
            dayDiv.addEventListener("dragover", (event) => event.preventDefault());
            dayDiv.addEventListener("drop", async (event) => {
                const taskId = event.dataTransfer.getData("taskId");
                await fetch("/update_task", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ id: parseInt(taskId), days: [i] }),
                });
            });
            ganttHeader.appendChild(dayDiv);
        }
    }

    loadTasks();
    setupGantt();
});
