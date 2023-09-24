import React, { useEffect, useState } from 'react';

function App() {
  const [menuItems, setMenuItems] = useState([]);
  const [captureName, setCaptureName] = useState('');
  const [currentReferenceImageId, setCurrentReferenceImageId] = useState(null);
  const [selectedButton, setSelectedButton] = useState(null);

  const fetchReferenceImages = () => {
    return fetch('/reference_images') // Add 'return' here
    .then(response => response.json())
    .then(data => {
      const sortedData = data.sort((a, b) => b.timestamp.localeCompare(a.timestamp));
      setMenuItems(sortedData);
  
      // Automatically select the first item only if no selection is already active
      if (sortedData.length > 0 && currentReferenceImageId === null) {
        setCurrentReferenceImageId(sortedData[0].id);
        setSelectedButton(sortedData[0].id);
      }
    })
    .catch(error => {
      console.error('Error fetching reference images:', error);
    });
  };

  // For initial data fetching and updating image source
  useEffect(() => {
    const imgElement = document.getElementById('videoFeed');
    const URL = currentReferenceImageId ? `/diff?reference_image_id=${currentReferenceImageId}` : '/video_grid';
    imgElement.src = URL;
  
    // Only fetch data when currentReferenceImageId is null (page initial load)
    if (currentReferenceImageId === null) {
      fetchReferenceImages(); // Fetch initial list
    }
  
  }, [currentReferenceImageId]);

  // For handling keyboard events
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (menuItems.length === 0) return; // No items to navigate

      let currentIndex = menuItems.findIndex(item => item.id === currentReferenceImageId);

      if (e.keyCode === 38) { // Up arrow key
        currentIndex = (currentIndex <= 0) ? menuItems.length - 1 : currentIndex - 1;
      } else if (e.keyCode === 40) { // Down arrow key
        currentIndex = (currentIndex >= menuItems.length - 1) ? 0 : currentIndex + 1;
      } else {
        return; // Not an up or down arrow key
      }

      const newSelectedItemId = menuItems[currentIndex].id;
      setCurrentReferenceImageId(newSelectedItemId);
      setSelectedButton(newSelectedItemId);
    };

    window.addEventListener('keydown', handleKeyDown);

    return () => {
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [menuItems, currentReferenceImageId]);

  const buttonStyle = {
    display: 'block',
    width: 'calc(100% - 20px)',
    padding: '10px',
    marginBottom: '5px',
    backgroundColor: '#007BFF',
    color: 'white',
    textAlign: 'center',
    borderRadius: '4px',
    wordWrap: 'break-word',
    cursor: 'pointer',
    boxSizing: 'border-box'
  };

  const saveButtonStyle = {
    ...buttonStyle,
    backgroundColor: '#007BFF'
  };

  const getButtonStyle = (id) => {
    return {
      ...buttonStyle,
      backgroundColor: selectedButton === id ? '#0056b3' : '#007BFF', // Change background color if selected
    };
  };

  const handleSave = () => {
    fetch('/reference_images', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: new URLSearchParams({
        'name': captureName
      })
    })
    .then(response => response.json())
    .then(data => {
      if (data.status === 'success') {
        // Clear the text box
        setCaptureName('');        
        // Refresh menu items
        fetchReferenceImages();
      } else {
        console.error('Error saving reference image:', data.message);
      }
    })
    .catch(error => {
      console.error('Error saving reference image:', error);
    });
  };

  const handleImageSelection = (id) => {
    setCurrentReferenceImageId(id);
    setSelectedButton(id); // Set the selected button
  };

  const handleDelete = (id) => {
    fetch(`/reference_images?id=${id}`, {
      method: 'DELETE',
    })
    .then(response => response.json())
    .then(data => {
      if (data.status === 'success') {
        // Refresh menu items
        fetchReferenceImages().then(() => {
          // If the deleted item was the current selection, select the first item.
          if (id === currentReferenceImageId && menuItems.length > 0) {
            const firstItemId = menuItems[0].id;
            setCurrentReferenceImageId(firstItemId);
            setSelectedButton(firstItemId);
          }
        });
      } else {
        console.error('Error deleting reference image:', data.message);
      }
    })
    .catch(error => {
      console.error('Error deleting reference image:', error);
    });
  };

  return (
    <div className="App" style={{ backgroundColor: 'black', height: '100vh', width: '100vw' }}>
      <div 
        style={{ 
          display: 'block', 
          position: 'fixed', 
          left: 0, 
          top: 0, 
          zIndex: 100, 
          width: '274px',
          height: '100vh',
          overflowY: 'auto',
          backgroundColor: 'black',
          boxSizing: 'border-box'
        }}
      >
        <input 
          type="text" 
          placeholder="<capture name>" 
          style={{
            width: 'calc(100% - 20px)',
            margin: '10px',
            boxSizing: 'border-box'
          }}
          value={captureName}
          onChange={e => setCaptureName(e.target.value)}
        />
        <div 
          style={saveButtonStyle} 
          onClick={handleSave}
        >
          Save
        </div>
        <ul style={{ padding: 0, margin: 0, listStyleType: 'none', boxSizing: 'border-box' }}>
          {menuItems.map((item, index) => (
            <li key={index} style={{ display: 'flex', alignItems: 'center' }}>
              <div 
                style={getButtonStyle(item.id)}  // Use the new function here
                onClick={() => handleImageSelection(item.id)} 
                onMouseOver={e => e.currentTarget.style.backgroundColor = '#0056b3'}
                onMouseOut={e => e.currentTarget.style.backgroundColor = selectedButton === item.id ? '#0056b3' : '#007BFF'}  // Revert to original color or keep selected color
              >
                {item.name} - {item.timestamp}
              </div>
              <svg 
                xmlns="http://www.w3.org/2000/svg" 
                width="48" 
                height="48" 
                fill="red" 
                className="bi bi-trash" 
                viewBox="0 0 24 24"
                onClick={() => handleDelete(item.id)} // Add onClick handler here
              >
                <path d="M9 9L15 15M15 9L9 15M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" stroke="#000000" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </li>
          ))}
        </ul>
      </div>

      <div style={{ marginLeft: '250px', width: 'calc(100% - 250px)', height: '100vh', position: 'fixed', top: 0, right: 0 }}>
        <img id="videoFeed" alt="Video Feed" style={{ width: '100%', height: '100%', objectFit: 'contain' }} />
      </div>
    </div>
  );
}

export default App;
