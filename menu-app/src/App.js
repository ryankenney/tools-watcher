import React, { useEffect, useState } from 'react';

function App() {
  const [menuVisible, setMenuVisible] = useState(false);

  // Attach event listener to listen for 'keydown' events
  useEffect(() => {
    function handleKeyDown(e) {
      if (['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight'].includes(e.code)) {
        setMenuVisible(true);
      }
    }
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  // Fetch video frame from Flask endpoint
  useEffect(() => {
    // Create an image element to handle multipart image stream
    const imgElement = document.getElementById('videoFeed');
    const URL = 'http://localhost:5000/video_grid';
    imgElement.src = URL;
  }, []);

  return (
    <div className="App">
      {/* Menu */}
      <div style={{ display: menuVisible ? 'block' : 'none', position: 'fixed', left: 0, top: 0, zIndex: 100 }}>
        <ul>
          <li>Menu Item 1</li>
          <li>Menu Item 2</li>
          <li>Menu Item 3</li>
        </ul>
      </div>

      {/* Video Feed */}
      <div style={{ marginLeft: menuVisible ? '150px' : '0' }}>
        <img id="videoFeed" alt="Video Feed" />
      </div>
    </div>
  );
}

export default App;