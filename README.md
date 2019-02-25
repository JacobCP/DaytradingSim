# Daytrading Simulation with Python

The simulation implements a low-risk daytrading strategy on historical stock data.  
For a high-level understanding of the strategy, see [this](https://www.linkedin.com/pulse/search-safe-day-trading-algorithm-jacob-ehrlichster) article.

### **To run the simulation yourself, you'll need historical trading data in the following format:**  

A CSV text file named \<stock-symbol\>.txt, with the \<stock-symbol\> being the trading symbol your data is for.  

The text file should have two columns - the first being the timestamp for the data (one that can be recognized by the pd.Timestamp() function), the second being the stock price at that time.
The file should have column headers, though their names don't matter.  

### **To run the simulation:**  

* place the text file in the stock_data directory.  
* set parameters for the simulation in the outline.py file.  
* pass outline.py to python to start the simulation.  
* simulation progress, basic information and results will print out in the console.   
* results will be saved in a <stock-symbol>_results directory.  
