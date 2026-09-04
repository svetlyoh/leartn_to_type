export const chooseDrill=<T extends {id:string}>(items:T[],seed:number)=>items[Math.abs(seed)%items.length];

