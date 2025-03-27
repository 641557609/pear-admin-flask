import unittest
from ..services.variable_service import VariableHandler

class Test(unittest.TestCase):
    def test_init(self):
        pass

    def test_extract_variables(self):
        variable_handler = VariableHandler()
        text = """
        select b.shopgroupid '运营体',b.dept_name '店铺',a.item_bh 'SKU',a.amount '数量',c.qc_time '单件质检时间'  from stor_dtl  a with(nolock)
        left join sys_department b with(nolock) on a.ovs_deptid = b.dept_code
        left join v_item_inf c on a.item_bh = c.item_bh where stor_wh_code = 'NH' and qc_dt>={{sdt}} and qc_dt<{{edt}}
         select c.GroupID '运营体',b.dept_name '店铺',a.ID '计划号',a.is_tax_included '是否含税',is_self_pickup '是否自提',ISNULL(is_consolidated, 0) '是否拼货',50 as '基数',15*a.is_tax_included as '是否含税系数',
         15*is_self_pickup as '是否自提系数',20*ISNULL(is_consolidated, 0) as '是否拼货系数',(50 +15*a.is_tax_included + 15*is_self_pickup+ 20*ISNULL(is_consolidated, 0))  '总系数','' as '难度分摊比例','' as '分摊费用' from ovs_use a left join SYS_Department b on a.depart_code = b.dept_code
         left join AreaGroup c on b.shopgroupid = c.GroupID where wh_id = 'NF' and Finish_Time >={{sdt}} and Finish_Time <{{edt}}
         
         select shopgroupid '运营体',dept_name '店铺',COUNT(temp.id) '发货计划数',sum(bin_num) '发货箱数',sum(sku_types) 'SKU种类数',sum(final_total_num) '发货件数',SUM(pack_total_time)/60 '计划单包装时长',
         (8*COUNT(temp.id)+ 9*sum(bin_num) + 20*sum(sku_types) + 3*sum(final_total_num) +SUM(pack_total_time)/60) as '复杂度','' as '分摊系数','' as '分摊金额'
         from (
        select b.shopgroupid, b.dept_name,a.id ,(select MAX(bin_bh) from ovs_use_bin where MainID = a.id) as bin_num ,count(distinct(c.item_bh)) sku_types,sum(final_num) final_total_num,SUM(d.package_take_time*c.final_num) as pack_total_time from ovs_use a with(nolock) 
        left join ovs_use_detail c with(nolock) on a.ID = c.MainID 
        left join SYS_Department b with(nolock) on a.depart_code = b.dept_code 
        left join stor_cur d with(nolock)  on c.Item_bh = d.item_bh and d.wh_id = 'NH'
        where a.wh_id = 'NH' and Finish_Time >={{sdt}} and Finish_Time<{{edt}}
        group by b.shopgroupid,b.dept_name,a.id ) as temp group by shopgroupid,dept_name
        select s.shopgroupid '运营体',s.dept_name '店铺',temp2.item_bh 'SKU',temp2.period '当月库龄',temp2.volume '体积',sum(temp2.rema_amt) '数量',(temp2.period*temp2.volume*sum(temp2.rema_amt)) as'系数' from (
        select DATEDIFF(DAY,case when dt < {{sdt}} then {{sdt}} else dt end,{{edt}}) as period, a.item_bh,a.item_nm, b.length,b.width,b.height,(b.length*b.width*b.height)*0.0001 as 'volume',a.rema_amt,a.ovs_deptid,1 as count_type  from stor_serial a with(nolock) 
        left join stor_cur b on a.item_bh = b.item_bh and a.stor_wh_id = b.wh_id where stor_wh_id = 'NH' and rema_amt>0 and dt<{{edt}} and b.length>0
        and ISNULL(a.ovs_deptid,'')<>''
        union all
        select DATEDIFF(DAY,case when c.dt < {{sdt}} then {{sdt}} else c.dt end,temp.Finish_Time+1),temp.sku,d.item_nm,b.length,b.width,b.height,(b.length*b.width*b.height)*0.0001 as 'volume',temp.amount,temp.ovs_deptid,2 as count_type from (
        select ISNULL(e.item_bh,a.item_bh) sku,ISNULL(e.serial,a.seriel) serial,ISNULL(e.amount,a.amount) amount,d.Finish_Time,a.ovs_deptid from stor_dtl_warehouse a with(nolock) left join ovs_use b with(nolock) on a.stor_bh = b.fh_stor_bh 
        left join stor_serial c with(nolock) on a.seriel =c.seriel 
        left join item_bom_serial e with(nolock) on a.stor_bh = e.stor_bh 
        left join ovs_use d with(nolock) on a.stor_bh = d.fh_stor_bh  where d.Finish_Time>={{sdt}} and d.Finish_Time<{{edt}} and b.wh_id = 'NH') temp 
        left join stor_cur b with(nolock) on temp.sku = b.item_bh and b.wh_id = 'NH'
        left join stor_serial c with(nolock) on temp.serial = c.seriel
        left join v_item_inf d on temp.sku = d.item_bh ) temp2 left join SYS_Department s with(nolock) on temp2.ovs_deptid = s.dept_code
        group by s.shopgroupid ,s.dept_name ,temp2.item_bh ,temp2.period ,temp2.volume
        """
        variables = variable_handler.extract_variables(text)
        print(variables)
    def test_resolve(self):
        variable_handler = VariableHandler()
        variables_config = [
            {"variable_name": "123",
             "variable_value": "LastMonthEnd",
             "variable_type": "timestamp"
             },
            {"variable_name": "234",
             "variable_value": "LastMonthEnd",
             "variable_type": "fixed"
             },
            {"variable_name": "345",
             "variable_value": "LastYearLastMonthStart",
             "variable_type": "timestamp"
             },
            {"variable_name": "456",
             "variable_value": "LastYearMonthEnd",
             "variable_type": "fixed"
             },
            {"variable_name": "567",
             "variable_value": "SELECT Name, JobNum, status FROM sys_user WHERE status = '1' AND ISNULL(jobNum, '') != ''",
             "variable_type": "sql"
             }
        ]
        variables = variable_handler.resolve(variables_config)
        print(variables)

