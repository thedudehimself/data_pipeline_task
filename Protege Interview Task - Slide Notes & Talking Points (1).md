#### **Slide 1: Title**

* **Action:** Introduce yourself, thank them for the opportunity, and state the presentation's title.

#### 

#### 

#### **Slide 2: The Objective**

* **Action:** Briefly walk through the agenda.

* "My goal today isn't just to show you the final code, but to demonstrate my approach to **problem-solving**—how I deconstruct a request, adapt when the initial plan fails, and build a solution designed for the long term."

#### 

#### 

#### **Slide 3: Deconstructing the Problem**

* **Action:** Explain the core task and the constraints.  
    
* "My first step in any project is to move from an ambiguous request to a clear set of business requirements. I presented a decision matrix of potential solutions and asked Richard for clarity on accuracy, budget, and timeline. Based on his feedback and the technical constraints \- a throttled API would take over 24 hours for data acquisition alone \- the hybrid approach \- webscraping labeled training data then using native language processing was the clear winner."

#### 

#### 

#### **Slide 4: Web Scraping & NLP Solution: Why and How**

* **Action:** Briefly explain the technical choices.  
    
* "The choice of tools was deliberate. This configuration—using TF-IDF \- Term Frequency \- Inverse Document Frequency and Logistic Regression—is a robust, industry-standard baseline for text classification. TF-IDF excels at highlighting the most descriptive keywords that differentiate one record from others in a corpus. It was chosen for its effectiveness and speed, perfectly matching the project's constraints of a 1-day turnaround." 

#### 

#### 

#### **Slide 5: The Journey Pt. 1: Foundational ETL**

* "I believe in a 'measure twice, cut once' approach. The initial discovery step was crucial because it informed the design of the entire pipeline and prevented future surprises. Identifying blockers before building is key, especially before re-engaging with a customer."

#### 

#### **Slide 6: The Journey Pt. 2: The "Aha\!" Moment**

* **Action:** Tell the story of the misleading metric.  
    
* "This highlights a core principle of my approach: metrics can be misleading, and it's our job to validate them. Rather than pushing forward with a model that looked good on paper but would have ultimately failed the customer, I paused to build additional diagnostics. This proactive step to identify the root cause—in this case, data bias—is crucial for de-risking a project and ensuring the final deliverable is truly valuable."

#### 

#### **Slide 7: The Journey Pt. 3: The Pivot to Intelligent Acquisition**

* **Action:** Explain how you solved the data bias problem with a smarter, more strategic approach.

#### 

#### **Slide 8: The Final Result & System Architecture**

* **Action:** Present the successful outcome and the final accuracy, explicitly mentioning that it exceeded the stretch goal.

#### 

#### **Slide 9: Key Features of the Final System**

* **Action:** Walk through the features that make this a professional, reusable system, not just a one-off script.

#### 

#### **Slide 10: Thank you!**

* "I built the solution this way because a one-off script only solves a problem once. This configurable, fully-automated pipeline is the first step toward a productized asset. We just need to add a listener watching for changes to a data store to automatically launch the pipeline. This is how you **unlock the engineering team** from solving the same problem repeatedly - Richard identified as a key challenge at Protege today.

By adding automated testing and a readily reproducible setup, we lay the groundwork for monitoring - invaluable for turning this pipeline into a service instrumental to Protege's long-term success."s