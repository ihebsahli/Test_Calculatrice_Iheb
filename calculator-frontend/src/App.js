import React from 'react';
import Calculator from './components/Calculator';
import './App.css';

const App = () => {
    return (
        <div>
            <h1 style={{ textAlign: 'center', margin: '20px 0', color: '#333' }}>Calculator</h1>
            <Calculator />
          
        </div>
    );
};

export default App;
