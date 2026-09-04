export const grossWpm=(correctChars:number,activeMs:number)=>activeMs<=0?0:(correctChars/5)/(activeMs/60000);
export const accuracy=(correct:number,attempts:number)=>attempts<=0?100:(correct/attempts)*100;
export const cadenceCv=(intervals:number[])=>{if(intervals.length<2)return null;const mean=intervals.reduce((a,b)=>a+b,0)/intervals.length;const variance=intervals.reduce((a,b)=>a+(b-mean)**2,0)/intervals.length;return mean===0?0:Math.sqrt(variance)/mean};
export const cadenceScore=(intervals:number[])=>{const cv=cadenceCv(intervals);return cv===null?null:Math.max(0,Math.min(100,100*(1-cv)))};

