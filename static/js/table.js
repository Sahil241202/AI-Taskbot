let editingId = null;
let tempData = {};
let customColumns = [];

document.addEventListener('DOMContentLoaded', () => {
    loadColumns();
    loadTasks();
});

async function loadTasks() {
    try {
        const response = await fetch('/tasks');
        const tasks = await response.json();
        renderTasks(tasks);
    } catch (error) {
        console.error('Error loading tasks:', error);
    }
}

function renderTasks(tasks) {
    const tbody = document.getElementById('taskBody');
    tbody.innerHTML = tasks.map(task => `
        <tr data-id="${task.id}">
            <td>${task.name}</td>
            <td>${task.assignee || ''}</td>
            <td><span class="status-pill ${task.status.toLowerCase().replace(' ', '-')}">${task.status}</span></td>
            <td>${task.due_date || ''}</td>
            <td><span class="priority-pill ${task.priority ? task.priority.toLowerCase() : 'none'}">${task.priority || 'None'}</span></td>
            ${customColumns.map(col => `
                <td>${task.custom_fields?.[col.name] || ''}</td>
            `).join('')}
            <td>
                <button class="edit-btn" onclick="startEditing(${task.id})">Edit</button>
                <button class="delete-btn" onclick="deleteTask(${task.id})">Delete</button>
            </td>
        </tr>
    `).join('');
}

function addNewTask() {
    const newRow = `
        <tr class="new-task">
            <td class="editable-cell"><input type="text" id="newName"></td>
            <td class="editable-cell"><input type="text" id="newAssignee"></td>
            <td class="editable-cell">
                <select id="newStatus">
                    <option>TO DO</option>
                    <option>IN PROGRESS</option>
                    <option>DONE</option>
                </select>
            </td>
            <td class="editable-cell"><input type="date" id="newDueDate"></td>
            <td class="editable-cell">
                <select id="newPriority">
                    <option value="">None</option>
                    <option>Urgent</option>
                    <option>High</option>
                    <option>Normal</option>
                    <option>Low</option>
                </select>
            </td>
            ${customColumns.map(col => `
                <td class="editable-cell"><input type="text" id="new${col.name.replace(/\s+/g, '')}"></td>
            `).join('')}
            <td>
                <button onclick="saveNewTask()">Save</button>
                <button onclick="cancelNewTask()">Cancel</button>
            </td>
        </tr>
    `;
    
    document.getElementById('taskBody').insertAdjacentHTML('afterbegin', newRow);
}

async function saveNewTask() {
    const taskData = {
        name: document.getElementById('newName').value,
        assignee: document.getElementById('newAssignee').value,
        status: document.getElementById('newStatus').value,
        due_date: document.getElementById('newDueDate').value,
        priority: document.getElementById('newPriority').value,
        custom_fields: customColumns.reduce((acc, col) => {
            acc[col.name] = document.getElementById(`new${col.name.replace(/\s+/g, '')}`).value;
            return acc;
        }, {})
    };

    try {
        const response = await fetch('/tasks', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(taskData)
        });
        
        if(response.ok) {
            loadTasks();
        }
    } catch (error) {
        console.error('Error saving task:', error);
    }
}

async function deleteTask(taskId) {
    if (confirm('Are you sure you want to delete this task?')) {
        try {
            const response = await fetch(`/tasks/${taskId}`, {
                method: 'DELETE'
            });
            
            if (response.ok) {
                loadTasks();
            } else {
                console.error('Delete failed:', await response.text());
            }
        } catch (error) {
            console.error('Delete error:', error);
        }
    }
}

function startEditing(taskId) {
    const row = document.querySelector(`tr[data-id="${taskId}"]`);
    const cells = row.cells;
    
    tempData = {
        name: cells[0].textContent,
        assignee: cells[1].textContent,
        status: cells[2].querySelector('.status-pill').textContent,
        due_date: cells[3].textContent,
        priority: cells[4].textContent,
        custom_fields: customColumns.reduce((acc, col, index) => {
            acc[col.name] = cells[5 + index].textContent;
            return acc;
        }, {})
    };

    cells[0].innerHTML = `<input value="${tempData.name}">`;
    cells[1].innerHTML = `<input value="${tempData.assignee}">`;
    cells[2].innerHTML = `
        <select class="status-select">
            <option ${tempData.status === 'TO DO' ? 'selected' : ''}>TO DO</option>
            <option ${tempData.status === 'IN PROGRESS' ? 'selected' : ''}>IN PROGRESS</option>
            <option ${tempData.status === 'DONE' ? 'selected' : ''}>DONE</option>
        </select>
    `;
    cells[3].innerHTML = `<input type="date" value="${tempData.due_date}">`;
    cells[4].innerHTML = `
        <select class="priority-select">
            <option value="">None</option>
            <option ${tempData.priority === 'Urgent' ? 'selected' : ''}>Urgent</option>
            <option ${tempData.priority === 'High' ? 'selected' : ''}>High</option>
            <option ${tempData.priority === 'Normal' ? 'selected' : ''}>Normal</option>
            <option ${tempData.priority === 'Low' ? 'selected' : ''}>Low</option>
        </select>
    `;
    customColumns.forEach((col, index) => {
        cells[5 + index].innerHTML = `<input value="${tempData.custom_fields[col.name]}">`;
    });

    cells[5 + customColumns.length].innerHTML = `
        <button onclick="saveTask(${taskId})">Save</button>
        <button onclick="cancelEdit(${taskId})">Cancel</button>
    `;

    editingId = taskId;
}

async function saveTask(taskId) {
    const row = document.querySelector(`tr[data-id="${taskId}"]`);
    const inputs = row.querySelectorAll('input, select');
    
    const updatedData = {
        name: inputs[0].value,
        assignee: inputs[1].value,
        status: inputs[2].value,
        due_date: inputs[3].value,
        priority: inputs[4].value,
        custom_fields: customColumns.reduce((acc, col, index) => {
            acc[col.name] = inputs[5 + index].value;
            return acc;
        }, {})
    };

    try {
        const response = await fetch(`/tasks/${taskId}`, {
            method: 'PUT',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(updatedData)
        });

        if (response.ok) {
            loadTasks();
            editingId = null;
        } else {
            console.error('Update failed:', await response.text());
        }
    } catch (error) {
        console.error('Update error:', error);
    }
}

function cancelEdit(taskId) {
    if (editingId === taskId) {
        loadTasks();
        editingId = null;
    }
}

function showColumnModal() {
    document.getElementById('columnModal').style.display = 'block';
}

function closeColumnModal() {
    document.getElementById('columnModal').style.display = 'none';
    document.getElementById('columnName').value = '';
    document.getElementById('columnOptions').value = '';
}

function toggleOptions() {
    const type = document.getElementById('columnType').value;
    document.getElementById('optionsSection').style.display = 
        type === 'select' ? 'block' : 'none';
}

async function createColumn() {
    const name = document.getElementById('columnName').value;
    const type = document.getElementById('columnType').value;
    const options = document.getElementById('columnOptions').value.split(',').map(o => o.trim());

    if (!name) {
        alert('Column name is required');
        return;
    }

    try {
        const response = await fetch('/columns', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                name: name,
                type: type,
                options: type === 'select' ? options : null
            })
        });
        
        if (response.ok) {
            loadColumns();
            closeColumnModal();
        }
    } catch (error) {
        console.error('Error creating column:', error);
    }
}

async function loadColumns() {
    try {
        const response = await fetch('/columns');
        customColumns = await response.json();
        updateTableHeaders();
        loadTasks();
    } catch (error) {
        console.error('Error loading columns:', error);
    }
}

function updateTableHeaders() {
    const thead = document.querySelector('.task-table thead tr');
    thead.innerHTML = `
        <th>NAME</th>
        <th>ASSIGNEE</th>
        <th>STATUS</th>
        <th>DUE DATE</th>
        <th>PRIORITY</th>
        ${customColumns.map(col => `<th>${col.name}</th>`).join('')}
        <th>ACTIONS</th>
    `;
}