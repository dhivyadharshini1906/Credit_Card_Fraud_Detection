const form=document.getElementById("transactionForm"), result=document.getElementById("result");
async function refresh(){
 try{
  const [sRes,tRes]=await Promise.all([fetch("/api/summary"),fetch("/api/transactions")]);
  const s=await sRes.json(), rows=await tRes.json();
  for(const [id,key] of [["totalCount","total"],["highCount","high_risk"],["mediumCount","medium_risk"],["lowCount","low_risk"]]) document.getElementById(id).textContent=s[key];
  document.getElementById("transactionRows").innerHTML=rows.length?rows.map(r=>`<tr><td>${r.id}</td><td>₹${Number(r.amount).toLocaleString("en-IN")}</td><td>${r.risk_score}%</td><td class="risk ${r.risk_level}">${r.risk_level}</td><td>${r.prediction}</td></tr>`).join(""):'<tr><td colspan="5">No transactions yet.</td></tr>';
 }catch(e){result.textContent="Unable to load dashboard. Check the server."}
}
form.addEventListener("submit",async e=>{
 e.preventDefault();const d=new FormData(form),button=document.getElementById("submitBtn");
 const payload={amount:Number(d.get("amount")),hour:Number(d.get("hour")),recent_transactions:Number(d.get("recent_transactions")),account_age_days:Number(d.get("account_age_days")),international:d.has("international"),online:d.has("online")};
 button.disabled=true;button.textContent="Analysing...";
 try{const res=await fetch("/api/predict",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(payload)});const out=await res.json();if(!res.ok)throw Error(out.detail||"Analysis failed");result.innerHTML=`<strong>${out.prediction}</strong> · Risk: ${out.risk_level} · Score: ${out.risk_score}%`;await refresh();}
 catch(err){result.textContent=err.message}finally{button.disabled=false;button.textContent="Analyse transaction"}
});
document.getElementById("refreshBtn").addEventListener("click",refresh);refresh();
