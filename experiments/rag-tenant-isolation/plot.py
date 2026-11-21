"""Regenerate three data-derived figures. No image assets are committed."""
import json
from pathlib import Path
import matplotlib.pyplot as plt
r=json.loads(Path("results.json").read_text(encoding="utf-8"))
m=r["metrics"]
ks=[v["k"] for v in m]
fig,ax=plt.subplots(figsize=(9,5))
ax.plot(ks,[v["post_target_pct"] for v in m],marker="o",label="Global ranking → permission filter")
ax.plot(ks,[v["pre_target_pct"] for v in m],marker="s",label="Authorize candidates → rank")
ax.set(xlabel="Top-k documents",ylabel="Correct target document retrieved (%)",
       title="Where the permission check happens changes retrieval")
ax.set_xticks(ks);ax.set_ylim(0,105);ax.grid(alpha=.25);ax.legend()
fig.tight_layout();fig.savefig("figure_1_retrieval.png",dpi=180);plt.close(fig)

fig,ax=plt.subplots(figsize=(9,4))
ax.axis("off")
ax.text(.02,.8,"GLOBAL SEARCH",weight="bold",fontsize=14)
ax.text(.02,.53,"All tenants → top-k → remove foreign chunks\nCan discard the correct document after ranking",fontsize=11)
ax.text(.53,.8,"AUTHORIZED SEARCH",weight="bold",fontsize=14)
ax.text(.53,.53,"Verified caller → permitted chunks → top-k\nOnly relevant, allowed records compete",fontsize=11)
ax.set_title("The authorization boundary must precede ranking")
fig.tight_layout();fig.savefig("figure_2_boundary.png",dpi=180);plt.close(fig)

fig,ax=plt.subplots(figsize=(9,4.6))
labels=["Global first result from foreign tenant","Late filter returned no target","Tenant-first retrieved target"]
counts=[next(v for v in m if v["k"]==5)["global_wrong_first"],
        768-next(v for v in m if v["k"]==5)["post_target"],
        next(v for v in m if v["k"]==5)["pre_target"]]
ax.barh(labels,counts);ax.set_xlim(0,805);ax.invert_yaxis()
for i,val in enumerate(counts): ax.text(val+8,i,str(val)+"/768",va="center")
ax.set_title("Observed outcomes in 768 fictional top-five queries")
fig.tight_layout();fig.savefig("figure_3_outcomes.png",dpi=180);plt.close(fig)
print("Generated 3 local PNG files.")
