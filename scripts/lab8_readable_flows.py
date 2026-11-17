"""Reader-facing flows: one complete graph per architecture, in plain Vietnamese.

The technical catalog remains available as the code review reference. This
module only describes documentation; it never executes a claim or a refund.
"""
from lab8_flow_catalog import n, e, p, flow, W, SA, O, SW, B, V, T, R, S, D, P, M, C, H

PALETTE = {
    "llm": ("AI MÔ PHỎNG · MockLLM", "#eee6ff", "#7545ad"),
    "python": ("LUẬT XỬ LÝ · Python", "#e5f3e9", "#247049"),
    "read": ("TRA CỨU DỮ LIỆU", "#e4f1ff", "#2d639f"),
    "host": ("CỔNG KIỂM SOÁT TIỀN", "#fff0d7", "#9c6118"),
    "sqlite": ("SỔ DỮ LIỆU · SQLite", "#e7ecf1", "#4b6277"),
    "result": ("KẾT QUẢ", "#eaf0d2", "#586728"),
    "crash": ("GIÁN ĐOẠN / LỖI", "#ffe8e3", "#a34736"),
}


def step(id, title, kind, row, col=1, detail="", file="", code="", decision=False):
    node=n(id,title,kind,row,col,detail,file,decision)
    node["reference"]=code
    return node


def complete(id,title,input,steps,owner,output,difference,files,nodes,edges,notes):
    return flow(id,title,input,steps,owner,output,difference,list(dict.fromkeys(files)),
                [p(id+"_whole",title+" — toàn bộ luồng",nodes,edges)],notes)


def settlement(q, row, file):
    """Expand the common settlement inline, not as a separate page/panel."""
    return [
        step(q+"positive","Có tiền được đề xuất hoàn?","python",row,decision=True,detail="Số tiền tính theo chính sách lớn hơn 0"),
        step(q+"zero","Từ chối hoàn tiền","result",row,0,detail="Không đủ điều kiện; không ghi khoản hoàn",file=C,code="finish(status='denied', proposal_amount=0)"),
        step(q+"host","Gửi đề xuất đến cổng kiểm soát tiền","host",row+1,detail="Kiểm quyền duyệt, giới hạn và khoản đã hoàn",file=D,code="issue_refund(claim_id, full_quote, crash_at=...)"),
        step(q+"ok","Cổng kiểm soát chấp nhận?","python",row+2,decision=True),
        step(q+"yes","Hoàn tiền thành công","result",row+2,0,detail="Có thể là kết quả đã lưu từ lần trước",file=C,code="finish(status='resolved', proposal_amount=full_quote)"),
        step(q+"conflict","Khác số tiền đã ghi trước đó?","python",row+3,decision=True),
        step(q+"failed","Báo lỗi và giữ khoản hoàn cũ","result",row+3,0,detail="Không ghi đè số tiền đã trả",file=file,code="outcome.conflict → failed"),
        step(q+"no","Từ chối và nêu lý do","result",row+4,detail="Giữ nguyên số tiền đề xuất; không tạo khoản hoàn mới",file=file,code="outcome.ok=False, conflict=False → denied"),
        step(q+"end","Trả kết quả và ghi nhật ký an toàn","python",row+5,detail="Kết quả dựa trên sổ tiền và nhật ký thật",file=C,code="finish(...) → RunResult"),
    ],[
        e(q+"positive",q+"zero","Không"),e(q+"positive",q+"host","Có"),e(q+"host",q+"ok"),
        e(q+"ok",q+"yes","Có"),e(q+"ok",q+"conflict","Không"),e(q+"conflict",q+"failed","Có"),
        e(q+"conflict",q+"no","Không"),e(q+"zero",q+"end"),e(q+"yes",q+"end"),e(q+"failed",q+"end"),e(q+"no",q+"end"),
    ]


wn,we=settlement("w",6,W)
FLOWS=[complete("workflow","Quy trình cố định · Workflow",
    "Mã yêu cầu hoàn tiền và dữ liệu đơn hàng trong hệ thống",
    "Tìm yêu cầu → kiểm tra chủ đơn → tính tiền → xin phép ghi khoản hoàn",
    "Python làm theo các bước cố định; không cần gọi AI",
    "Hoàn tiền, từ chối, xin thêm thông tin, chuyển xử lý hoặc báo lỗi",
    "Đơn giản và dễ kiểm soát: số tiền luôn được tính bằng luật đã viết sẵn.",[W,T,S,C,D],[
        step("wstart","Tìm yêu cầu của khách hàng","read",0,file=T,code="get_claim_view(claim_id)"),
        step("wfound","Tìm thấy yêu cầu?","python",1,decision=True),
        step("wunknown","Báo lỗi: không có yêu cầu này","result",1,0,file=S,code="failed / unknown_claim"),
        step("wid","Khách đã cung cấp mã đơn hàng?","python",2,decision=True),
        step("wneed","Xin khách bổ sung mã đơn hàng","result",2,0,detail="Không đoán mã đơn từ lời nhắn",file=S,code="needs_info"),
        step("wread","Tra cứu đơn và kiểm tra người sở hữu","read",3,file=T,code="lookup_order(order_id, principal_id)"),
        step("wvisible","Được phép xem đơn hàng này?","python",4,decision=True),
        step("wesc","Chuyển yêu cầu sang xử lý phù hợp","result",4,0,detail="Đơn không tìm thấy hoặc thuộc người khác",file=S,code="escalated"),
        step("wquote","Tính số tiền được hoàn theo chính sách","read",5,detail="Chọn khoản lớn hơn giữa hoàn phí giao hàng và bồi thường",file=T,code="compute_compensation → compensation.quote"),
        *wn,
    ],[
        e("wstart","wfound"),e("wfound","wunknown","Không"),e("wfound","wid","Có"),e("wid","wneed","Không"),e("wid","wread","Có"),
        e("wread","wvisible"),e("wvisible","wesc","Không"),e("wvisible","wquote","Có"),e("wquote","wpositive"),*we,
    ],["Lời nhắn của khách không thay thế dữ liệu đơn hàng. Không tự cộng hai loại bồi thường.",
        "Số tiền đề xuất có thể khác tiền thực trả, vì cổng kiểm soát còn trừ khoản đã hoàn và áp dụng giới hạn."])]

sn,se=settlement("s",12,SA)
FLOWS.append(complete("single","Một tác nhân làm từng bước · Single ReAct",
    "Yêu cầu đã được đọc cùng bộ nhớ ban đầu rỗng",
    "Quan sát → nhờ AI mô phỏng suy nghĩ → Python chọn việc → đọc dữ liệu → quan sát tiếp",
    "Python chọn hành động; lời AI trả về không quyết định bước tiếp theo",
    "Kết luận sớm, dừng sau tối đa 8 lượt, hoặc gửi đề xuất cho cổng kiểm soát tiền",
    "Có vòng lặp nhưng quyền hành động vẫn bị giới hạn; AI không tự chọn số tiền hay ghi khoản hoàn.",[SA,R,M,T,S],[
        step("sstart","Đọc yêu cầu và khởi tạo bộ nhớ","read",0,file=SA,code="get_claim_view; state={}; observation={'claim':claim}"),
        step("slimit","Còn lượt trong giới hạn 8 lần?","python",1,decision=True,file=R,code="run_react(max_steps=8)"),
        step("scap","Dừng và báo lỗi vì vượt giới hạn","result",1,0,file=R,code="failed / step_cap"),
        step("smemory","Ghi nhớ kết quả vừa tra cứu","python",2,detail="Nếu đã có kết quả từ lượt trước",file=SA,code="decide: state[last_tool]=last_result"),
        step("sthink","Nhờ AI mô phỏng một lượt suy nghĩ","llm",3,detail="Tính đủ số lượt gọi và chi phí mô phỏng",file=M,code="complete(purpose='react'); Budget.add_llm"),
        step("schoose","Python chọn việc tiếp theo từ dữ liệu","python",4,detail="Bỏ qua nội dung lời AI trả về",file=SA,code="decide(observation)"),
        step("sfinal","Đã đủ kết quả hoặc có lý do phải dừng?","python",5,decision=True),
        step("sorder","Đã đọc thông tin đơn hàng?","python",6,decision=True),
        step("sreadorder","Tra cứu đơn và người sở hữu","read",6,0,file=R,code="dispatch: lookup_order"),
        step("sreadquote","Tính tiền theo dữ liệu và chính sách","read",7,file=R,code="dispatch: compute_compensation"),
        step("sobserve","Đưa kết quả đọc vào lượt tiếp theo","python",8,file=R,code="seen={last_tool,last_result,claim}"),
        step("shasquote","Có kết quả tính tiền để xét hoàn?","python",9,0,decision=True,file=SA,code="if 'quote' in final"),
        step("sstop","Trả lời theo lý do đã xác định","result",10,0,detail="Xin mã đơn, chuyển xử lý hoặc báo yêu cầu không tồn tại",file=SA,code="needs_info / escalated / failed"),
        step("ssettle","Tiếp tục xét đề xuất hoàn tiền","python",11,file=S,code="ClaimRun.settle(final['quote'], crash_at)"),
        *sn,
    ],[
        e("sstart","slimit"),e("slimit","scap","Không"),e("slimit","smemory","Có"),e("smemory","sthink"),e("sthink","schoose"),e("schoose","sfinal"),
        e("sfinal","shasquote","Có"),e("sfinal","sorder","Không"),e("sorder","sreadorder","Không"),e("sorder","sreadquote","Có"),
        e("sreadorder","sobserve"),e("sreadquote","sobserve"),e("sobserve","slimit","Lượt tiếp theo",True),
        e("shasquote","sstop","Không"),e("shasquote","ssettle","Có"),e("ssettle","spositive"),*se,
    ],["Ngay cả lượt kết luận cũng gọi AI mô phỏng trước khi Python quyết định. Lượt AI này không xuất lệnh để chạy công cụ.",
        "Yêu cầu bình thường đi qua ba lượt: đọc đơn, tính tiền, kết luận. Tám lượt là giới hạn bảo vệ của hệ thống."]))

on,oe=settlement("o",12,O)
FLOWS.append(complete("orchestrator","Bộ điều phối và bộ tra cứu · Orchestrator",
    "Yêu cầu của khách hàng và phạm vi đơn hàng được phép xem",
    "Kiểm tra đầu vào → mô phỏng lập kế hoạch → giao việc chỉ đọc → tập hợp kết quả → xét hoàn tiền",
    "Bộ điều phối giữ quyền quyết định; bộ tra cứu chỉ đọc dữ liệu",
    "Kết quả xử lý yêu cầu, với khoản hoàn do cổng kiểm soát cho phép",
    "Phân vai rõ ràng nhưng bộ tra cứu vẫn chạy tuần tự, không chạy song song.",[O,R,H,T,M,S],[
        step("ostart","Đọc yêu cầu của khách hàng","read",0,file=T,code="get_claim_view"),
        step("ofound","Yêu cầu tồn tại?","python",1,decision=True),step("ofail","Báo lỗi: yêu cầu không tồn tại","result",1,0,file=S,code="failed"),
        step("oid","Đã có mã đơn hàng?","python",2,decision=True),step("oneed","Xin khách bổ sung mã đơn hàng","result",2,0,file=S,code="needs_info"),
        step("oplan","Nhờ AI mô phỏng lập kế hoạch","llm",3,file=M,code="complete(purpose='plan')"),
        step("ohandoff","Giao việc với quyền chỉ đọc","python",4,detail="Chỉ gửi thông tin và công cụ được phép",file=H,code="make_handoff: handoff.v1, allowlist"),
        step("oinvestigate","Bộ tra cứu đọc dữ liệu theo thứ tự","read",5,detail="Đọc yêu cầu → đọc đơn → đọc chính sách",file=R,code="run_readonly_investigators; worker=True"),
        step("ocanquote","Có đơn hàng được phép đọc?","python",6,decision=True),
        step("ocompute","Bộ tra cứu tính tiền theo chính sách","read",7,file=T,code="dispatch: compute_compensation"),
        step("oreturn","Gửi kết quả về bộ điều phối","python",8,file=R,code="return claim_view + tools"),
        step("ovisible","Kết quả có đơn hàng hợp lệ?","python",9,decision=True),step("oesc","Chuyển sang xử lý phù hợp","result",9,0,detail="Không gọi AI tổng hợp hay cổng ghi tiền",file=S,code="escalated"),
        step("oaggregate","Nhờ AI mô phỏng tổng hợp kết quả","llm",10,detail="Số tiền vẫn lấy từ kết quả tính bằng code",file=M,code="complete(purpose='aggregate')"),
        step("osettle","Bộ điều phối xét đề xuất hoàn tiền","python",11,file=S,code="ClaimRun.settle"),*on,
    ],[
        e("ostart","ofound"),e("ofound","ofail","Không"),e("ofound","oid","Có"),e("oid","oneed","Không"),e("oid","oplan","Có"),
        e("oplan","ohandoff"),e("ohandoff","oinvestigate"),e("oinvestigate","ocanquote"),e("ocanquote","ocompute","Có"),e("ocanquote","oreturn","Không"),
        e("ocompute","oreturn"),e("oreturn","ovisible"),e("ovisible","oesc","Không"),e("ovisible","oaggregate","Có"),e("oaggregate","osettle"),e("osettle","opositive"),*oe,
    ],["Bộ tra cứu không được tạo phiếu duyệt hoặc ghi tiền. Hệ thống từ chối cấp công cụ ghi cho vai trò này.",
        "Hai lần gọi AI chỉ mô phỏng lập kế hoạch và tổng hợp; các lời trả về không thay đổi danh sách công cụ hay cách tính tiền."]))


def swarm_flow(verified):
    q="b" if verified else "r";file=B if verified else SW
    nodes=[
        step(q+"start","Tìm yêu cầu và đọc lời nhắn của khách","read",0,file=file,code="_run: SELECT selected claim fields"),
        step(q+"found","Tìm thấy yêu cầu?","python",1,decision=True),step(q+"unknown","Báo lỗi: không có yêu cầu này","result",1,0,file=C,code="failed / unknown_claim"),
        step(q+"peer","Nhờ AI mô phỏng một ý kiến ban đầu","llm",2,file=M,code="complete(purpose='peer')"),
        step(q+"parsepy","Python đọc số ngày khách nói bị trễ","python",3,file=M,code="parse_delay_days(ticket)"),
        step(q+"parseai","Nhờ AI mô phỏng việc đọc lời nhắn","llm",4,detail="Số ngày dùng tiếp là kết quả Python đã đọc",file=M,code="complete(purpose='parse'); text ignored"),
        step(q+"id","Đã có mã đơn hàng?","python",5,decision=True),step(q+"need","Nhờ AI soạn lời xin thêm mã đơn","llm",5,0,detail="Kết thúc: cần bổ sung thông tin",file=file,code="draft → finish(needs_info)"),
        step(q+"investigate","Tra cứu đơn, chính sách và tính tiền","read",6,detail="Chỉ đọc; lần lượt từng việc, không chạy song song",file=R,code="make_handoff → run_readonly_investigators"),
        step(q+"visible","Đơn thuộc phạm vi được phép đọc?","python",7,decision=True),step(q+"esc","Nhờ AI soạn lời chuyển xử lý","llm",7,0,detail="Không ghi tiền; chuyển yêu cầu đến nơi phù hợp",file=file,code="draft → finish(escalated)"),
        step(q+"weak","Rơi vào lần mô phỏng có lỗi cố ý?","python",8,decision=True,detail="Khách nói khác dữ liệu và mã mô phỏng chia hết cho 5",file=file,code="parsed_delay differs; seed % 5 == 0"),
        step(q+"override","Tin số ngày của khách và tính tiền lại","python",9,0,detail="Đây là lỗi được cài sẵn để làm đối chứng",file=file,code="order.delay_days=parsed_delay; compute_compensation"),
        step(q+"candidate","Nhận số tiền đề xuất hiện tại","python",10,detail="Có thể đã sai vì tin lời nhắn thay cho dữ liệu",file=file,code="quote_payload"),
    ]
    edges=[e(q+"start",q+"found"),e(q+"found",q+"unknown","Không"),e(q+"found",q+"peer","Có"),e(q+"peer",q+"parsepy"),e(q+"parsepy",q+"parseai"),
        e(q+"parseai",q+"id"),e(q+"id",q+"need","Không"),e(q+"id",q+"investigate","Có"),e(q+"investigate",q+"visible"),e(q+"visible",q+"esc","Không"),
        e(q+"visible",q+"weak","Có"),e(q+"weak",q+"override","Có"),e(q+"weak",q+"candidate","Không"),e(q+"override",q+"candidate")]
    row=11
    if verified:
        nodes += [
            step("bfresh","Đọc lại đơn từ nguồn dữ liệu đáng tin","read",11,detail="Kiểm lại cả quyền sở hữu của khách",file=V,code="verify_order → dispatch lookup_order(worker=True)"),
            step("bfound","Vẫn đọc được đơn hàng này?","python",12,decision=True),
            step("breject","Đặt số tiền về 0 để tránh ghi nhầm","python",12,0,detail="Ghi lại lý do không thể kiểm chứng",file=V,code="verifier_rejected; verifier_order_not_visible"),
            step("bcheck","Đối chiếu ba dữ kiện quan trọng","python",13,detail="Số ngày trễ · trạng thái đơn · hỏng hàng đã xác minh",file=V,code="delay_days, status, damage_verified; verifier_check"),
            step("bmatch","Cả ba dữ kiện đều khớp?","python",14,decision=True),
            step("bkeep","Giữ nguyên số tiền đã tính","python",14,0,detail="Không cần tính lại",file=V,code="return candidate, quote_payload"),
            step("brepair","Tính lại đúng một lần từ dữ liệu thật","read",15,detail="Ghi nhận việc sửa và số tiền trước, sau",file=V,code="compute_compensation(trusted); verifier_override; repair_round=1"),
            step("bverified","Nhận số tiền sau kiểm chứng","python",16,detail="Ví dụ T02: đề xuất sai 20.000 được sửa về 0",file=B,code="verify_order returns corrected quote"),
        ]
        edges += [e("bcandidate","bfresh"),e("bfresh","bfound"),e("bfound","breject","Không"),e("bfound","bcheck","Có"),
            e("bcheck","bmatch"),e("bmatch","bkeep","Có"),e("bmatch","brepair","Không"),e("brepair","bverified"),e("bkeep","bverified"),e("breject","bverified")]
        row=17
    nodes.append(step(q+"draft","Nhờ AI mô phỏng soạn lời phản hồi","llm",row,detail="AI không chọn số tiền và không ghi khoản hoàn",file=M,code="complete(purpose='draft')"))
    edges.append(e("bverified" if verified else "rcandidate",q+"draft"))
    ns,es=settlement(q,row+1,file);nodes+=ns;edges += [e(q+"draft",q+"positive"),*es]
    notes=["Đây là luồng mô phỏng tuần tự: ý kiến AI → Python đọc số ngày → AI đọc lời nhắn → tra cứu → phản hồi. Không có trao đổi hai chiều hoặc nhiều người làm cùng lúc.",
        "Lời AI trả về không quyết định tiền. Cổng ghi tiền vẫn kiểm duyệt và giới hạn, nhưng không tính lại quyền được bồi thường."]
    if verified:
        notes += ["T02, mã mô phỏng 55: khách nói trễ 5 ngày, đơn thật ghi 2 ngày. Bước kiểm chứng sửa đề xuất 20.000 về 0, rồi từ chối hoàn tiền.",
            "Kiểm chứng dữ kiện luôn diễn ra trước khi xét số tiền bằng 0 và trước khi ghi tiền. Không đọc được đơn để kiểm chứng thì luồng hiện tại trả số tiền 0 và từ chối."]
    else:
        notes += ["T02, mã mô phỏng 55: đơn thật trễ 2 ngày nhưng khách nói 5 ngày. Lỗi cố ý tạo đề xuất sai 20.000; cổng ghi tiền không tự sửa dữ kiện này."]
    return complete("b3" if verified else "swarm","Nhiều vai mô phỏng + kiểm chứng · B3" if verified else "Nhiều vai mô phỏng tuần tự · Swarm",
        "Yêu cầu, lời nhắn khách hàng và dữ liệu đơn hàng",
        "Đọc → mô phỏng ý kiến → tra cứu → kiểm chứng dữ kiện → phản hồi → xét hoàn" if verified else "Đọc → mô phỏng ý kiến → tra cứu → thử lỗi cố ý → phản hồi → xét hoàn",
        "Python kiểm chứng dữ kiện; cổng kiểm soát quyết quyền ghi tiền" if verified else "Python chạy các bước; AI chỉ mô phỏng trao đổi và soạn lời",
        "Kết quả xử lý yêu cầu cùng số tiền thực được phép ghi",
        "Có một lần kiểm chứng độc lập trước mọi quyết định ghi tiền." if verified else "Cố ý giữ một lỗi tin lời khách để so sánh độ tin cậy.",
        [file,M,R,T,D,V] if verified else [file,M,R,T,D],nodes,edges,notes)


FLOWS.append(swarm_flow(False))

FLOWS.append(complete("host","Cổng kiểm soát và ghi tiền · Host",
    "Yêu cầu và toàn bộ số tiền đề xuất, chưa tự trừ khoản hoàn trước đó",
    "Kiểm chủ đơn → kiểm phiếu duyệt → trừ khoản đã hoàn và giới hạn tiền → chống ghi trùng → lưu an toàn",
    "Code của cổng kiểm soát quyết quyền ghi; cơ sở dữ liệu bảo đảm lưu tiền và nhật ký cùng nhau",
    "Chấp nhận, từ chối, báo xung đột số tiền hoặc truyền lỗi để bộ chạy xử lý",
    "Không tính lại quyền bồi thường; kiểm duyệt và giới hạn tiền trước khi kiểm khoản hoàn cũ.",[D,P,S,C],[
        step("hstart","Nhận yêu cầu ghi khoản hoàn","host",0,detail="Giữ riêng tiền đề xuất và tiền thực sẽ trả",file=D,code="issue_refund(claim_id, proposed_vnd, crash_at)"),
        step("hclaim","Yêu cầu có tồn tại?","host",1,decision=True),step("hunknown","Từ chối: không có yêu cầu này","result",1,0,detail="Nhánh này không ghi nhật ký từ chối chính sách",file=D,code="unknown_claim; no policy_denied"),
        step("howner","Có đơn hàng đúng người yêu cầu?","host",2,decision=True,detail="Phải có mã đơn, tìm thấy đơn và đúng chủ",file=D,code="claim.order_id; orders.principal_id == claim.principal_id"),
        step("hhistory","Đọc tổng tiền các yêu cầu khác đã hoàn","sqlite",3,file=P,code="order_refunded_vnd(exclude_claim_id=claim_id)"),
        step("happroval","Đọc đúng phiếu duyệt của yêu cầu này","sqlite",4,file=P,code="claims.approval_id → approvals"),
        step("hvalid","Phiếu duyệt hợp lệ và tiền dương?","host",5,decision=True,detail="Đúng yêu cầu, chưa thu hồi, còn hạn; tiền duyệt và đề xuất đều dương",file=P,code="authorize: claim match → valid status → expiry → positive amounts"),
        step("hcap","Trừ tiền đã hoàn và áp dụng giới hạn","host",6,detail="Không vượt tiền được duyệt hoặc phần khách đã trả còn lại",file=P,code="proposed-already; min(approved); min(paid-already)"),
        step("hpositive","Sau khi giới hạn vẫn còn tiền để trả?","host",7,decision=True),
        step("hdeny","Ghi lý do từ chối, không hoàn thêm","host",5,0,detail="Sai chủ đơn, phiếu duyệt không hợp lệ hoặc đã hoàn đủ",file=D,code="record_policy_denied → outcome.ok=False"),
        step("hcrashone","Có thử dừng trước khi ghi tiền?","host",8,decision=True,file=D,code="crash_at == before_effect"),
        step("hstopone","Gián đoạn khi chưa ghi khoản mới","crash",8,0,file=D,code="InjectedCrash('before_effect')"),
        step("hexisting","Yêu cầu này đã có khoản hoàn?","host",9,decision=True,file=D,code="get_refund(claim_id)"),
        step("hequal","Số tiền cũ khớp số vừa được duyệt?","host",9,0,decision=True,file=D,code="existing.amount_vnd == decision.amount_vnd"),
        step("hconflict","Báo xung đột, giữ nguyên khoản cũ","result",10,0,file=D,code="_audit_conflict; conflict=True → shape failed"),
        step("hreplay","Dùng lại kết quả đã lưu, không trả thêm","host",7,0,detail="Cập nhật điểm khôi phục rồi trả thành công",file=D,code="_checkpoint(existing); idempotent_replay"),
        step("hlock","Bắt đầu lượt ghi có khóa bảo vệ","sqlite",10,file=D,code="BEGIN IMMEDIATE"),
        step("hstable","Lịch sử hoàn tiền vẫn chưa thay đổi?","host",11,decision=True,detail="Đọc lại trong lúc giữ khóa ghi",file=D,code="re-read order_refunded_vnd == already"),
        step("hretry","Hủy lượt ghi; còn một lần thử lại?","host",11,0,decision=True,file=D,code="rollback; if _retry"),
        step("htryagain","Chạy lại từ đầu với dữ liệu mới","host",12,0,detail="Chỉ tự thử lại một lần",file=D,code="issue_refund(..., _retry=False)"),
        step("hchanged","Từ chối vì lịch sử tiếp tục thay đổi","result",13,0,file=D,code="policy_denied / order_total_changed"),
        step("hsave","Lưu khoản hoàn và nhật ký cùng nhau","sqlite",12,detail="Cùng một giao dịch: hoặc lưu cả hai, hoặc không lưu",file=D,code="INSERT refund_ledger + refund_committed audit; commit"),
        step("hcrashtwo","Có thử dừng sau khi đã ghi tiền?","host",13,decision=True,file=D,code="crash_at == after_effect_before_checkpoint"),
        step("hstoptwo","Gián đoạn: tiền và nhật ký đã lưu","crash",14,0,detail="Chưa kịp lưu điểm khôi phục mới",file=D,code="InjectedCrash('after_effect_before_checkpoint')"),
        step("hcheckpoint","Lưu điểm khôi phục của yêu cầu","sqlite",14,file=D,code="_checkpoint(effect); commit separately"),
        step("hcrashthree","Có thử dừng sau điểm khôi phục?","host",15,decision=True,file=D,code="crash_at == after_checkpoint"),
        step("hstopthree","Gián đoạn sau khi đã lưu đầy đủ","crash",16,0,file=D,code="InjectedCrash('after_checkpoint')"),
        step("hdone","Xác nhận hoàn tiền thành công","result",16,detail="Trả số thực ghi; số đề xuất vẫn được giữ riêng",file=D,code="outcome.ok=True, reason='committed'; shape resolved"),
        step("hresume","Bộ chạy gọi lại cùng yêu cầu và dữ liệu","python",18,0,detail="Không tạo khoản thứ hai nếu số tiền còn khớp",file="src/tests/test_public_matrix.py",code="run_claim(... same DB, crash_at=None)"),
    ],[
        e("hstart","hclaim"),e("hclaim","hunknown","Không"),e("hclaim","howner","Có"),e("howner","hdeny","Không"),e("howner","hhistory","Có"),
        e("hhistory","happroval"),e("happroval","hvalid"),e("hvalid","hdeny","Không"),e("hvalid","hcap","Có"),e("hcap","hpositive"),e("hpositive","hdeny","Không"),
        e("hpositive","hcrashone","Có"),e("hcrashone","hstopone","Có"),e("hcrashone","hexisting","Không"),e("hexisting","hequal","Có"),e("hexisting","hlock","Không"),
        e("hequal","hconflict","Không"),e("hequal","hreplay","Có"),e("hlock","hstable"),e("hstable","hretry","Không"),e("hstable","hsave","Có"),
        e("hretry","htryagain","Có"),e("hretry","hchanged","Không"),e("htryagain","hstart","Thử lại một lần",True),
        e("hsave","hcrashtwo"),e("hcrashtwo","hstoptwo","Có"),e("hcrashtwo","hcheckpoint","Không"),e("hcheckpoint","hcrashthree"),
        e("hcrashthree","hstopthree","Có"),e("hcrashthree","hdone","Không"),e("hstopone","hresume"),e("hstoptwo","hresume"),e("hstopthree","hresume"),e("hresume","hstart","Chạy lại sau gián đoạn",True),
    ],["Cổng này kiểm quyền ghi và giới hạn tiền; không tự tính lại khách có thực sự đủ điều kiện bồi thường hay không.",
       "Ví dụ: đề xuất bồi thường 150.000, đơn đã nhận 30.000, thì chỉ trả thêm 120.000 nếu các giới hạn khác cho phép.",
       "Nếu đã có khoản hoàn, vẫn phải kiểm lại phiếu duyệt và tiền trước khi dùng lại kết quả. Dùng lại kết quả không đi qua điểm thử dừng sau điểm khôi phục.",
       "Nếu cơ sở dữ liệu báo ghi trùng: hủy lượt ghi, đọc khoản hiện có rồi dùng lại nếu khớp; khác tiền thì báo xung đột. Lỗi không xử lý được được truyền ra ngoài, không giả báo thành công."]))

FLOWS.append(swarm_flow(True))

COMPARISON=[
    ["Quy trình cố định", "Làm theo các bước Python đã viết sẵn", "Không cần gọi AI", "Cổng kiểm soát ghi tiền", "Có kết quả hoặc gặp nhánh phải dừng", "Sai luật hoặc sai dữ liệu đầu vào"],
    ["Một tác nhân", "Lặp: quan sát, chọn việc, tra cứu", "Mô phỏng suy nghĩ; lời trả về không chọn hành động", "Cổng kiểm soát, nằm ngoài vòng chọn công cụ", "Có kết luận hoặc đủ 8 lượt", "Chọn sai việc, mất thông tin hoặc vượt số lượt"],
    ["Bộ điều phối", "Giao việc chỉ đọc rồi tập hợp kết quả", "Mô phỏng lập kế hoạch và tổng hợp", "Bộ điều phối gọi cổng; bộ tra cứu không ghi", "Đầu vào thiếu, không đọc được đơn hoặc đã xét xong", "Giao thiếu thông tin, cấp sai quyền, thêm chi phí"],
    ["Nhiều vai mô phỏng", "Các vai lần lượt xử lý, không chạy song song", "Mô phỏng ý kiến, đọc lời nhắn và soạn phản hồi", "Cổng kiểm soát ghi tiền", "Thiếu thông tin, không đọc được đơn hoặc đã xét xong", "Lỗi cố ý tin số ngày khách nói thay cho dữ liệu thật"],
]
