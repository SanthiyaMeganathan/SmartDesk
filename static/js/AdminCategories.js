document.addEventListener("DOMContentLoaded", () => {
    resetForm(); 
});

// Handle clicking a color swatch
document.querySelectorAll('.color-swatch').forEach(swatch => {
    swatch.addEventListener('click', function(e) {
        if(this.classList.contains('disabled')) {
            e.preventDefault();
            return; 
        }
        document.querySelectorAll('.color-swatch').forEach(s => s.classList.remove('selected'));
        this.classList.add('selected');
        this.querySelector('input').checked = true;
    });
});

// Switch form to Edit Mode
function openEditMode(id, name, desc, color) {
    document.getElementById('formTitle').innerText = "Edit category";
    document.getElementById('editCatId').value = id;
    document.getElementById('catName').value = name;
    document.getElementById('catDesc').value = desc;
    
    document.getElementById('submitBtn').innerHTML = '<i class="ri-save-line"></i> Save changes';
    document.getElementById('cancelBtn').style.display = 'inline-flex';

    // Reset all colors to their default backend state first
    document.querySelectorAll('.color-swatch').forEach(s => {
        s.classList.remove('selected');
        if(s.classList.contains('backend-disabled')) {
            s.classList.add('disabled');
            if (s.querySelector('input')) s.querySelector('input').disabled = true;
        }
    });

    // UNLOCK the color currently owned by this category so they can keep it
    const targetSwatch = document.querySelector(`.color-swatch[data-color="${color}"]`);
    if(targetSwatch) {
        targetSwatch.classList.remove('disabled');
        targetSwatch.querySelector('input').disabled = false;
        targetSwatch.classList.add('selected');
        targetSwatch.querySelector('input').checked = true;
    }
}

// Reset form to Add Mode
function resetForm() {
    document.getElementById('formTitle').innerText = "Add new category";
    document.getElementById('editCatId').value = "";
    document.getElementById('addCategoryForm').reset();
    
    document.getElementById('submitBtn').innerHTML = '<i class="ri-add-line"></i> Add category';
    document.getElementById('cancelBtn').style.display = 'none';

    // Re-disable colors that are owned by categories
    document.querySelectorAll('.color-swatch').forEach(s => {
        s.classList.remove('selected');
        if(s.classList.contains('backend-disabled')) {
            s.classList.add('disabled');
            if (s.querySelector('input')) s.querySelector('input').disabled = true;
        } else {
            if (s.querySelector('input')) s.querySelector('input').disabled = false;
        }
    });

    // Auto-select first available color
    const availableSwatches = document.querySelectorAll('.color-swatch:not(.disabled)');
    if(availableSwatches.length > 0) {
        availableSwatches[0].classList.add('selected');
        availableSwatches[0].querySelector('input').checked = true;
    }
}

// Handle Form Submit (Add or Edit)
async function submitCategory() {
    const form = document.getElementById('addCategoryForm');
    const id = document.getElementById('editCatId').value;
    const name = form.category_name.value.trim();
    const desc = form.description.value.trim();
    const colorInput = form.querySelector('input[name="color"]:checked');

    if(!name) return alert("Please enter a category name.");
    if(!colorInput || !colorInput.value) return alert("Please select an available color. If none are available, you've reached the limit!");

    // Alert for modifying existing category
    const isEdit = id ? true : false;
    if (isEdit) {
        if(!confirm(`Alert: You are about to modify the existing category "${name}". Continue?`)) return;
    }

    const payload = { category_name: name, description: desc, color: colorInput.value };
    const url = id ? `/edit-category/${id}` : '/add-category';

    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        
        const data = await response.json();
        
        if(data.status === 'success') {
            // Success Pop-up
            alert(`Category "${name}" ${isEdit ? 'updated' : 'created'} successfully!`);
            window.location.reload(); 
        } else {
            alert("Error: " + data.message);
        }
    } catch (error) {
        alert("Failed to connect to the server.");
    }
}

// Handle Delete
async function deleteCategory(id, ticketCount, catName) {
    // Check if category has tickets
    if (ticketCount > 0) {
        if(!confirm(`ALERT: This category has ${ticketCount} ticket(s). Once deleted, it cannot be retrieved and will be deleted everywhere. Are you sure you want to proceed?`)) return;
    } else {
        if(!confirm(`Are you sure you want to delete the "${catName}" category?`)) return;
    }

    try {
        const response = await fetch(`/delete-category/${id}`, { method: 'DELETE' });
        const data = await response.json();
        
        if(data.status === 'success') {
            // Success Pop-up
            alert(`Category "${catName}" deleted successfully!`);
            window.location.reload();
        } else {
            alert("Error: " + data.message);
        }
    } catch (error) {
        alert("Failed to delete category.");
    }
}