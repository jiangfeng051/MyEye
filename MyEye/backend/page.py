#date:2018/8/8

class PageHelp:
    def __init__(self,current_page,total_count,base_url,per_page=10):
         self.current_page = current_page
         self.total_count = total_count
         self.base_url = base_url
         self.per_page = per_page

    @property
    def db_start(self):
        return (self.current_page-1)*self.per_page


    def total_page(self):
        v ,a = divmod(self.total_count,self.per_page)
        if a != 0:
            v += 1
        return v

    def paper_list(self):
        v = self.total_page()
        print(v)
        if v <=9:
            pager_range_start=1
            pager_range_end=v+1
        else:
            if self.current_page <=5:
                pager_range_start=1
                pager_range_end=9+1
            elif self.current_page > v-4:
                pager_range_start = v -8
                pager_range_end = v +1
            else:
                pager_range_start = self.current_page -4
                pager_range_end = self.current_page +5
        print( pager_range_start, pager_range_end)
        page_dict = {}
        if self.current_page ==1:
            page_dict['上一页'] = 'javascript:void(0);'
        else:
            page_dict['上一页'] = '%s?page=%s' % (self.base_url,self.current_page-1)
        for i in range(pager_range_start,pager_range_end):
            page_dict[i]= '%s?page=%s' % (self.base_url,i)
        if self.current_page ==v:
            page_dict['下一页'] = 'javascript:void(0);'
        else:
            page_dict['下一页'] = '%s?page=%s' % (self.base_url,self.current_page+1)
        return page_dict


if __name__ == '__main__':
    obj = PageHelp(1,1,'rule.html')
    print(obj.paper_list())

