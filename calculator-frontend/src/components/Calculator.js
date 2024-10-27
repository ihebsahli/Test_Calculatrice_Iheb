import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './Calculator.css';

const API_URL = 'http://localhost:8000';

const Calculator = () => {
    const [expression, setExpression] = useState('');
    const [result, setResult] = useState(null);
    const [history, setHistory] = useState([]);

    const handleButtonClick = (value) => {
        setExpression((prev) => prev + (prev ? ' ' : '') + value);
    };

    const handleCalculate = async () => {
        console.log('Calculating...');
        const exprArray = expression.trim().split(' '); // Trim pour enlever les espaces

        // Vérifiez si l'expression est vide
        if (exprArray.length === 0 || expression.trim() === '') {
            alert('Expression cannot be empty! Please enter a valid RPN expression.');
            return;
        }



        // Vérifiez si tous les éléments sont valides (nombres ou opérateurs)
        for (const item of exprArray) {
            if (isNaN(item) && !['+', '-', '*', '/'].includes(item)) {
                alert(`Invalid character detected: "${item}". Please use only numbers and operators (+, -, *, /).`);
                return;
            }
        }

        try {
            const response = await axios.post(`${API_URL}/calculate`, {
                expression: exprArray,
            });

            if (response && response.data) {
                console.log(response.data);
                setResult(response.data.result);
                fetchHistory();
            } else {
                console.error('Response or response data is undefined');
            }
        } catch (error) {
            console.error('There was an error!', error);
            if (error.response) {
                console.error('Response data:', error.response.data);
            } else if (error.request) {
                console.error('Request data:', error.request);
            } else {
                console.error('Error message:', error.message);
            }
        }
    };


    const handleClear = () => {
        setExpression('');
        setResult(null);
    };


    const handleExport = async () => {
        try {
            const response = await axios.get(`${API_URL}/export-csv`, {
                responseType: 'blob',
            });

            // Créer un lien pour télécharger le fichier CSV
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', 'operations.csv');
            document.body.appendChild(link);
            link.click();
            link.remove();
        } catch (error) {
            console.error('There was an error exporting the history!', error);
        }
    };


    const fetchHistory = async () => {
        try {
            const response = await axios.get(`${API_URL}/history`);
            setHistory(response.data);
        } catch (error) {
            console.error('There was an error fetching history!', error);
        }
    };


    const handleDeleteHistory = async () => {
        try {
            await axios.delete(`${API_URL}/history`);
            setHistory([]);
            console.log('History deleted successfully');
        } catch (error) {
            console.error('There was an error deleting history!', error);
        }
    };

    useEffect(() => {
        fetchHistory();
    }, []);

    return (
        <div className="calculator">
            <input
                type="text"
                value={expression}
                onChange={(e) => setExpression(e.target.value)}
                placeholder="Enter expression in RPN (e.g. 5 3 +)"
            />
            <div className="button-container">
                {['7', '8', '9', '/'].map((button) => (
                    <button key={button} onClick={() => handleButtonClick(button)}>
                        {button}
                    </button>
                ))}
                {['4', '5', '6', '*'].map((button) => (
                    <button key={button} onClick={() => handleButtonClick(button)}>
                        {button}
                    </button>
                ))}
                {['1', '2', '3', '-'].map((button) => (
                    <button key={button} onClick={() => handleButtonClick(button)}>
                        {button}
                    </button>
                ))}
                {['0', 'C', '=', '+'].map((button) => (
                    <button
                        key={button}
                        onClick={button === 'C' ? handleClear : button === '=' ? handleCalculate : () => handleButtonClick(button)}
                        className={
                            button === 'C' ? 'button-clear' :
                                button === '=' ? 'button-calculate' : ''
                        }
                    >
                        {button}

                    </button>
                ))}

                <button onClick={handleExport}>Export History</button>

                <button className="button-delete" onClick={handleDeleteHistory}>Delete History</button>
            </div>
            {result !== null ? (
                <p>Result: {result}</p>
            ) : (
                <p>Please enter an expression and click Calculate.</p>
            )}
            <h2>History</h2>
            <div className="history-container">
                <ul>
                    {history.map((op, index) => (
                        <li key={index} className="history-item">
                            {op.expression} = {op.result}
                        </li>
                    ))}
                </ul>
            </div>
        </div>
    );
};

export default Calculator;
