export const groups = [
 {title:'01 / Personal & symptoms',desc:'Basic profile and reported symptom categories',fields:[
  {key:'age',label:'Age',unit:'years',type:'number',min:1,max:120,placeholder:'e.g. 52',help:'Age in completed years'},
  {key:'sex',label:'Sex (dataset code)',type:'select',options:[[0,'0 · Female'],[1,'1 · Male']],help:'Encoding used by the training dataset'},
  {key:'cp',label:'Chest pain category',type:'select',options:[[0,'0 · Category 0'],[1,'1 · Category 1'],[2,'2 · Category 2'],[3,'3 · Category 3']],help:'Dataset category codes; clinical definitions require codebook verification'}]},
 {title:'02 / Clinical measurements',desc:'Resting measurements and exercise response',fields:[
  {key:'trestbps',label:'Resting blood pressure',unit:'mmHg',type:'number',min:1,max:350,placeholder:'e.g. 125'},
  {key:'chol',label:'Serum cholesterol',unit:'mg/dL',type:'number',min:1,max:1000,placeholder:'e.g. 212'},
  {key:'fbs',label:'Fasting blood sugar > 120 mg/dL',type:'select',options:[[0,'0 · No'],[1,'1 · Yes']]},
  {key:'restecg',label:'Resting ECG code',type:'select',options:[[0,'0 · Code 0'],[1,'1 · Code 1'],[2,'2 · Code 2']]},
  {key:'thalach',label:'Maximum heart rate',unit:'bpm',type:'number',min:1,max:300,placeholder:'e.g. 168'},
  {key:'exang',label:'Exercise-induced angina',type:'select',options:[[0,'0 · No'],[1,'1 · Yes']]}]},
 {title:'03 / Exercise & diagnostic codes',desc:'Additional encoded variables used by the model',fields:[
  {key:'oldpeak',label:'ST depression (oldpeak)',type:'number',min:0,max:20,step:'0.1',placeholder:'e.g. 1.0'},
  {key:'slope',label:'ST segment slope code',type:'select',options:[[0,'0 · Code 0'],[1,'1 · Code 1'],[2,'2 · Code 2']]},
  {key:'ca',label:'Major vessels code',type:'select',options:[[0,'0 · Code 0'],[1,'1 · Code 1'],[2,'2 · Code 2'],[3,'3 · Code 3'],[4,'4 · Code 4']]},
  {key:'thal',label:'Thalassemia test code',type:'select',options:[[0,'0 · Code 0'],[1,'1 · Code 1'],[2,'2 · Code 2'],[3,'3 · Code 3']]}
 ]}
];
export const sample={age:52,sex:1,cp:0,trestbps:125,chol:212,fbs:0,restecg:1,thalach:168,exang:0,oldpeak:1,slope:2,ca:0,thal:2};
export const labels={age:'Age',sex:'Sex',cp:'Chest pain',trestbps:'Blood pressure',chol:'Cholesterol',fbs:'Fasting glucose',restecg:'Resting ECG',thalach:'Maximum heart rate',exang:'Exercise angina',oldpeak:'ST depression',slope:'ST slope',ca:'Major vessels',thal:'Thalassemia'};
export function readable(raw){return String(raw||'').replace(/^(num__|cat__)/,'').replace(/^(0\.00 < |0\.00 <= )/,'').replace(/ <= 1\.00/g,' = 1').replace(/ <= 0\.00/g,' = 0').replace(/ > 0\.72/g,' > 0.72 (scaled)').replace(/([a-z]+)_([0-9]+)/g,(_,k,v)=>`${labels[k]||k} · code ${v}`).replace(/\b(age|sex|cp|trestbps|chol|fbs|restecg|thalach|exang|oldpeak|slope|ca|thal)\b/g,k=>labels[k]||k);}
