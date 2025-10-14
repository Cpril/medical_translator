# Report

## Critical Analysis

### Design Analysis

Most translators for example, Google Translate, provide a single free-form textbox and a raw translation. They don’t shape the care journey, suggest clinically useful responses, or explain what to expect from the U.S. healthcare process. Users must know what to ask next.

Our design is a translation device that support both **realtime translation** and **hospital preparation**. The translations are **context and role-aware**, implemented with structured output, using Gemini API (gemini-flash-latest modle).

How our design impacts human flourishing:
- Privacy & Trust: 
    - Compared to other hospital assistance services (such as "find a doctor" supported by ZocDoc), our hospital preperation doesn't ask for personal information, which protects the privacy of users. While we are aware of the drawback of this limitation, we think a choice worth making. 

- Equity & Access:
    - Compared to some hospital supported realtime translators, which have a limited number of supported languages, our project supports languages like Twi alongside Chinese and Urdu. 
    - Our project is also easy to access for non-english speakers compared to other hospital assistant applications or realtime translator services which asks for a lot more information before providing service. 

### Alternative Envisioning

We could have also done: 
- **pre-visit intake chatbot**: patient inputs symptoms,  medical history, and quick questions in their native language (Chinese/Urdu/Twi).​
- **LLM summarization**: analyzes the entire native-language conversation, summarizing it into a concise, bulleted English summary of the "Chief Complaint" and key risks (e.g., allergies, chronic conditions).​
- **Hospital Visit Outcome Summary**: Clinician reviews the standardized English summary before the patient arrives, allowing them to formulate a diagnostic plan and focus the in-person interaction.

These alternative designs can be benefitial to reduce visit stress, improve efficiency for hospital staff, and enhence data collection. However, it also contain risks of requiring advice from AI, depersonalization between patients and hospital staff, and data privicy concerns. 

We think the skill and resources we have now are unable to address these important drawbacks in these alternative designs.

## Technical Evaluation
### Systematic Testing
- We imagined what it would be like sending our parents to a clinic here in the US, which prompted us to implement the features "I'm at the hospital and need real time translation". As we think of "what brings a person to the hospital?" we added an assistance feature "I need to go to the hospital". 
- Since we are each proficient in one language in this model (other than English), we tested the model preformance in development according to its **accuracy** and **relevance to context**. 

### Performance Analysis
Strength: 
- Accurate
- Context aware: aware of hospital setting and expresses uncertainty.
- Concise/speedy: achieved after some iterations
Limitations: 
- Limited in details on some outside factors such as insurance coverage. (this is intentional as we are concerned about data privacy and ease of access)
- Right now only support 3 languages. 

## User Centered Design: 
### Prototype, User Testing, & Iterations
- Our first prototype includes features: realtime translation (only one-directional), hospital preperation (no structured output). 
- As we conducted user testing, our model preformed well in accuracy and comprehensiveness, but also revealed many **problems**: 

- It has high latency. While we know that during development, it was during user testing we realized how akward it is to wait.

- The realtime translation lacks clear direction such that it's unclear as to whether the translation is hospital to patient or patient to hospital. 

- Output is long and contain unnecessary material. This hinders user experience as they would have to read a lot of text. 

From these feedbacks, we implemented **solutions**: 

- We did prompt engineering to make output more concise. 

- We implemented structured output to further make the speed faster and eliminate unnecenssary materials

- We split real-time translation between two parts: hospital to patients and patients to hospital.

- The feedback on the unclear instruction also reminded us to add instruction so that user know how to user our application. Therefore we added instruction/disclaimer about data privacy as well. 

## Reflection: 
As international students, we've all experienced some moments of fustration when we weren't able to communicate with others or be understood by others. For the most part, this experience has prompted us to also experience kindness and empathy from others, such that we form relationship and friendship dispite language barriors. However, we understand that's not the case for everyone and everywhere. We are especially aware of those who might have disability, struggles with mental health, or dealling with cultural shock, on top of language barriors. These other factors may prevent them from being able to ask questions and sort out miscommunications personally, which is where our product can be very helpful. 