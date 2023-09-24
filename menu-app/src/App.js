import React, { useEffect, useState } from 'react';

function App() {
  const [menuItems, setMenuItems] = useState([]);
  const [captureName, setCaptureName] = useState('');

  const fetchReferenceImages = () => {
    fetch('http://localhost:5000/reference_images')
      .then(response => response.json())
      .then(data => {
        setMenuItems(data);
      })
      .catch(error => {
        console.error('Error fetching reference images:', error);
      });
  };

  useEffect(() => {
    const imgElement = document.getElementById('videoFeed');
    const URL = 'http://localhost:5000/video_grid';
    imgElement.src = URL;
    
    // Fetch initial list
    fetchReferenceImages();
  }, []);

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
    backgroundColor: 'red'
  };

  const handleSave = () => {
    fetch('http://localhost:5000/reference_images', {
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


  return (
    <div className="App" style={{ backgroundColor: 'black', height: '100vh', width: '100vw' }}>
      <div 
        style={{ 
          display: 'block', 
          position: 'fixed', 
          left: 0, 
          top: 0, 
          zIndex: 100, 
          width: '250px',
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
            <li key={index}>
              <div 
                style={buttonStyle}
                onMouseOver={e => e.currentTarget.style.backgroundColor = '#0056b3'}
                onMouseOut={e => e.currentTarget.style.backgroundColor = '#007BFF'}
              >
                {item.name} - {item.timestamp}
              </div>
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
