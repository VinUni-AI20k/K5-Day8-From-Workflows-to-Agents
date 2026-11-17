"""Build six Mermaid diagrams and a dependency-free offline SVG viewer.

Usage: python scripts/build_flow_docs.py
Only docs/ and presentation/ are written. No lab module or report is executed.
"""
import html
import json
from pathlib import Path
import textwrap

from lab8_readable_flows import COMPARISON, FLOWS, PALETTE

ROOT = Path(__file__).resolve().parents[1]
LINK_BLOCK = """\n<!-- lab8-flow-links:start -->\n## Luồng xử lý chi tiết — phụ lục\n\nSơ đồ tổng quan được giữ trong [architecture.md](architecture.md). Sáu luồng được diễn giải bằng tiếng Việt dễ đọc trong [phụ lục Mermaid](flow_details.md): [quy trình cố định](flow_details.md#workflow), [một tác nhân](flow_details.md#single), [bộ điều phối](flow_details.md#orchestrator), [nhiều vai mô phỏng](flow_details.md#swarm), [cổng ghi tiền](flow_details.md#host), [kiểm chứng B3](flow_details.md#b3).\n\nĐọc từ trái sang phải. Trên HTML, mỗi lựa chọn hiển thị toàn bộ luồng trong một sơ đồ liền mạch, không chia phần hay chuyển trang. Có zoom, xem trọn luồng và mở rộng; toàn bộ hình nằm sẵn trong file local. Tên hàm và đường dẫn được chuyển xuống bảng đối chiếu kỹ thuật.\n<!-- lab8-flow-links:end -->\n"""


def wrap(text, width):
    return [line for part in text.split("\n") for line in textwrap.wrap(part, width=width, break_long_words=True, break_on_hyphens=False)]


def geometry(node):
    title = wrap(node["title"], 34 if node["decision"] else 40)
    detail = wrap(node["detail"], 45)
    source = []  # Keep code paths in the technical reference, not in reader labels.
    height = max(240 if node["decision"] else 150, 52 + len(title)*29 + len(detail)*23)
    return dict(x=360+node["row"]*720, y=220+node["col"]*410,
                w=600 if node["decision"] else 530, h=height,
                title=title, detail=detail, source=source)


def svg_panel(flow, panel):
    nodes = {x["id"]: x for x in panel["nodes"]}
    geo = {key: geometry(node) for key, node in nodes.items()}
    width = max(g["x"]+g["w"]/2 for g in geo.values())+100
    minx = min(g["x"]-g["w"]/2 for g in geo.values())-85
    # Keep a margin for feedback paths; no dynamic layout dependency is required.
    width = max(width, 1500)
    height = max(g["y"]+g["h"]/2 for g in geo.values())+180
    uid = panel["id"]
    title = html.escape(flow["title"]+" — toàn bộ quy trình")
    content = [f'<title id="{uid}-title">{title}</title>',
        f'<desc id="{uid}-desc">Nút hình thoi là quyết định, nhánh Có/Không. Nhãn loại và màu phân biệt quyền hạn; đọc từ trái sang phải, các nhánh kết thúc nằm phía trên.</desc>',
        f'<defs><marker id="{uid}-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 Z" fill="#6c7e79"/></marker></defs>']
    # Left-to-right layout. Side exits lead to terminal branches; feedback
    # and long joins use the outside corridor, away from intermediate nodes.
    for i, edge in enumerate(panel["edges"]):
        a,b=geo[edge["source"]],geo[edge["target"]]
        label=edge["label"]
        if a["x"] == b["x"]:
            sign=1 if b["y"]>a["y"] else -1
            x1,y1=a["x"],a["y"]+sign*a["h"]/2
            x2,y2=b["x"],b["y"]-sign*b["h"]/2
            points=[(x1,y1),(x2,y2)]
            lx,ly=x1+50,(y1+y2)/2
        elif edge.get("back") or b["x"] < a["x"]:
            lane=height-35-(i%3)*20
            x1,y1=a["x"],a["y"]+a["h"]/2
            x2,y2=b["x"],b["y"]+b["h"]/2
            points=[(x1,y1),(x1,lane),(x2,lane),(x2,y2)]
            lx,ly=(x1+x2)/2,lane-15
        elif a["y"] == b["y"]:
            x1,y1=a["x"]+a["w"]/2,a["y"]
            x2,y2=b["x"]-b["w"]/2,b["y"]
            intervening=any(g["y"]==a["y"] and a["x"]<g["x"]<b["x"] for g in geo.values())
            if intervening:
                lane=height-35-(i%3)*20
                points=[(a["x"],a["y"]+a["h"]/2),(a["x"],lane),(b["x"],lane),(b["x"],b["y"]+b["h"]/2)]
                lx,ly=(x1+x2)/2,lane-15
            else:
                points=[(x1,y1),(x2,y2)]
                lx,ly=(x1+x2)/2,y1-20
        else:
            x1,y1=a["x"]+a["w"]/2,a["y"]
            x2,y2=b["x"]-b["w"]/2,b["y"]
            if b["x"]-a["x"]>720:
                lane=height-35-(i%3)*20
                points=[(a["x"],a["y"]+a["h"]/2),(a["x"],lane),(b["x"],lane),(b["x"],b["y"]+b["h"]/2)]
                lx,ly=(x1+x2)/2,lane-15
            else:
                mid=(x1+x2)/2
                points=[(x1,y1),(mid,y1),(mid,y2),(x2,y2)]
                lx,ly=mid+35,(y1+y2)/2-15
        d="M "+" L ".join(f"{x:.1f},{y:.1f}" for x,y in points)
        content.append(f'<path d="{d}" fill="none" stroke="#6c7e79" stroke-width="2.4" marker-end="url(#{uid}-arrow)"/>')
        if label:
            lines=wrap(label,23)
            for k,line in enumerate(lines):
                content.append(f'<text x="{lx}" y="{ly+k*22}" text-anchor="middle" font-size="19" font-weight="700" fill="#3d514b" stroke="white" stroke-width="7" paint-order="stroke">{html.escape(line)}</text>')
    for key,node in nodes.items():
        g=geo[key];x,y,w,h=(g[k] for k in ("x","y","w","h"))
        tag,fill,stroke=PALETTE[node["kind"]]
        attrs=f'fill="{fill}" stroke="{stroke}" stroke-width="2.5"'
        if node["decision"]:
            # Wide rhombus, with the text in its central rectangular region.
            content.append(f'<polygon points="{x},{y-h/2} {x+w/2},{y} {x},{y+h/2} {x-w/2},{y}" {attrs}/>')
        elif node["kind"]=="sqlite":
            content.append(f'<path d="M{x-w/2},{y-h/2+17} C{x-w/2},{y-h/2-7} {x+w/2},{y-h/2-7} {x+w/2},{y-h/2+17} V{y+h/2-17} C{x+w/2},{y+h/2+7} {x-w/2},{y+h/2+7} {x-w/2},{y+h/2-17} Z" {attrs}/>')
            content.append(f'<path d="M{x-w/2},{y-h/2+17} C{x-w/2},{y-h/2+42} {x+w/2},{y-h/2+42} {x+w/2},{y-h/2+17}" fill="none" stroke="{stroke}" stroke-width="1.5"/>')
        else:
            content.append(f'<rect x="{x-w/2}" y="{y-h/2}" width="{w}" height="{h}" rx="{30 if node["kind"]=="result" else 9}" {attrs}/>')
        all_lines=[(tag,13,stroke,"700")]
        all_lines += [(s,24,"#182c2c","700") for s in g["title"]]
        all_lines += [(s,18,"#233f36","400") for s in g["detail"]]
        all_lines += [(s,16,"#42554c","400") for s in g["source"]]
        total=sum(font+6 for _,font,_,_ in all_lines)
        ty=y-total/2
        for line,font,color,weight in all_lines:
            ty+=font
            content.append(f'<text x="{x}" y="{ty:.1f}" text-anchor="middle" font-size="{font}" font-weight="{weight}" fill="{color}">{html.escape(line)}</text>')
            ty+=6
    body="".join(content)
    def make_svg(top=0, tile_height=None, prefix=""):
        h=tile_height or height
        parts=body.replace(uid+"-",prefix+uid+"-") if prefix else body
        return f'<svg xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="{prefix}{uid}-title {prefix}{uid}-desc" viewBox="{minx} {top} {width-minx} {h}" width="{width-minx}" height="{h}" style="font-family:Arial,Segoe UI,sans-serif;background:white">{parts}</svg>'
    return make_svg()


def mermaid(flow):
    lines=["flowchart LR"]
    for panel in flow["panels"]:
        lines.append(f'  subgraph panel_{panel["id"]}["{html.escape(panel["title"])}"]')
        for node in panel["nodes"]:
            tag=PALETTE[node["kind"]][0]
            label="<br/>".join(html.escape(s,quote=True) for s in
                [f"[{tag}] {node['title']}",node["detail"]] if s)
            if node["decision"]:
                shape='{'+f'"{label}"'+'}'
            elif node["kind"]=="sqlite":
                shape='[("'+label+'")]'
            else:
                shape='["'+label+'"]'
            lines.append(f'    {node["id"]}{shape}:::{node["kind"]}')
        for edge in panel["edges"]:
            label=f'|"{html.escape(edge["label"],quote=True)}"|' if edge["label"] else ""
            lines.append(f'    {edge["source"]} -->{label} {edge["target"]}')
        lines.append("  end")
    for kind,(_,fill,stroke) in PALETTE.items():
        lines.append(f"  classDef {kind} fill:{fill},stroke:{stroke},color:#182c2c,stroke-width:2px")
    return "\n".join(lines)


def validate():
    assert len(FLOWS)==6
    for flow in FLOWS:
        seen=set()
        for file in flow["files"]:
            assert (ROOT/file).is_file(),file
        for panel in flow["panels"]:
            ids={n["id"] for n in panel["nodes"]}
            assert not seen.intersection(ids), f"duplicate node in {flow['id']}"
            seen.update(ids)
            for edge in panel["edges"]:
                assert edge["source"] in ids and edge["target"] in ids
            for node in panel["nodes"]:
                assert node["kind"] in PALETTE
                if node["file"]:
                    assert (ROOT/node["file"]).exists(),node["file"]
                if node["decision"]:
                    labels={edge["label"] for edge in panel["edges"] if edge["source"]==node["id"]}
                    assert labels=={"Có","Không"}, (flow["id"],node["id"],labels)


def comparison_md():
    headers=["Kiến trúc","Điều phối","Vai trò MockLLM","Quyền ghi","Điều kiện dừng","Rủi ro"]
    return "\n".join(["| "+" | ".join(headers)+" |","| "+" | ".join(["---"]*6)+" |"]+
                      ["| "+" | ".join(row)+" |" for row in COMPARISON])


def build():
    validate()
    docs=["# Phụ lục — Sáu luồng xử lý Lab 08", "",
          "Sinh từ `scripts/lab8_readable_flows.py` bằng `python scripts/build_flow_docs.py`. Sơ đồ dùng ngôn ngữ dễ đọc; mỗi kiến trúc là một luồng đầy đủ, không chia thành từng phần. [Báo cáo chính](../report/team/group_report.md) · [Tổng quan kiến trúc](architecture.md) · [HTML offline](../presentation/index.html#flows).",
          "", "## Chú giải và cách đọc", "",
          "Hình thoi là câu hỏi Có/Không. Nhãn và màu cùng giúp phân biệt: AI mô phỏng (tím), luật xử lý Python (xanh lá), tra cứu dữ liệu (xanh dương), cổng kiểm soát tiền (cam), sổ dữ liệu SQLite (xám), kết quả (olive), gián đoạn/lỗi (đỏ). Tên hàm và đường dẫn nằm ở bảng kỹ thuật sau mỗi hình, giúp người đọc tập trung vào việc đang xảy ra.",
          "", "Tên kết quả trong chương trình: hoàn thành = resolved; cần thêm thông tin = needs_info; chuyển xử lý = escalated; từ chối = denied; lỗi = failed. ‘Số tiền đề xuất’ là khoản tính theo chính sách; ‘tiền thực trả’ là khoản sau khi xét quyền duyệt và giới hạn. Khi bị gián đoạn, bộ chạy gọi lại cùng dữ liệu để khôi phục, không tự trả thêm tiền.",
          "", "## So sánh bốn kiến trúc", "",comparison_md(),""]
    catalog=[]
    for flow in FLOWS:
        docs += [f'<a id="{flow["id"]}"></a>',f'## {flow["title"]}',"",
                 f'- **Đầu vào:** {flow["input"]}.',f'- **Các bước:** {flow["steps"]}.',
                 f'- **Ai quyết định:** {flow["owner"]}.',f'- **Đầu ra:** {flow["output"]}.',
                 f'- **Khác biệt:** {flow["difference"]}',"",
                 "Đối chiếu: "+", ".join(f"[`{f}`](../{f})" for f in flow["files"])+".","",
                 "```mermaid",mermaid(flow),"```",""]
        item={key:value for key,value in flow.items() if key!="panels"}
        assert len(flow["panels"])==1, "Each reader-facing flow must be one complete graph"
        panel=flow["panels"][0]
        item["svg"]=svg_panel(flow,panel)
        item["node_count"]=len(panel["nodes"])
        item["direction"]="LR"
        item["technical"]=[{"step":node["title"],"file":node["file"],"code":node.get("reference","")}
                           for node in panel["nodes"] if node["file"]]
        docs += ["### Đối chiếu kỹ thuật", "", "Các nhãn trong hình là diễn giải thân thiện; bảng này giữ liên kết với chương trình.", "",
                 "| Bước trong hình | Hàm hoặc nhánh tương ứng | File |", "| --- | --- | --- |"]
        docs += [f"| {r['step']} | `{r['code'].replace('|','/ ')}` | [`{r['file']}`](../{r['file']}) |" for r in item["technical"]]
        docs += [""]
        docs += ["- "+note for note in flow["notes"]]+[""]
        catalog.append(item)
    (ROOT/"docs/flow_details.md").write_text("\n".join(docs).strip()+"\n",encoding="utf-8")
    encoded=json.dumps({"flows":catalog,"comparison":COMPARISON,"legend":[
        {"kind":k,"tag":v[0],"fill":v[1],"stroke":v[2]} for k,v in PALETTE.items()]},ensure_ascii=False).replace("<","\\u003c")
    (ROOT/"presentation/flows-data.js").write_text("// Generated documentation only; benchmark data is untouched.\nwindow.LAB_FLOWS = "+encoded+";\n",encoding="utf-8")
    for name in ("architecture.md","report.md","bonus_report.md"):
        path=ROOT/"docs"/name
        if not path.exists():
            continue
        text=path.read_text(encoding="utf-8")
        start=text.find("<!-- lab8-flow-links:start -->")
        stop=text.find("<!-- lab8-flow-links:end -->")
        if start>=0 and stop>=start:
            text=text[:start]+text[stop+len("<!-- lab8-flow-links:end -->"):]
        elif "## Luồng xử lý chi tiết — phụ lục" in text:
            # Migrate the first generated appendix link block (this patch only).
            text=text[:text.index("## Luồng xử lý chi tiết — phụ lục")]
        path.write_text(text.rstrip()+"\n"+LINK_BLOCK,encoding="utf-8")
    print(f"Built {len(catalog)} reader-friendly complete diagrams; one SVG per flow, no benchmark changes")


if __name__=="__main__":
    build()
