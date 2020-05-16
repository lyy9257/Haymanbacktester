



class get_summary_data():

    def __init__(self):
        

    ## 성과지표 만들기
    def get_result(self, result_data):
        
        ## 성과지표 제작용 데이터 호출
        total_profit_data = result_data['total']

        ## CAGR 계산
        start = 1
        end = total_profit_data.iloc[-1]/100 + 1

        year = int(len(total_profit_data.index)/250)
        cagr = round(((end / start) ** (1/year)-1) * 100, 2)

        ## MDD 계산
        arr_v = np.array(total_profit_data)
        peak_lower = np.argmax(np.maximum.accumulate(arr_v) - arr_v)
        peak_upper = np.argmax(arr_v[:peak_lower])
        mdd = round((arr_v[peak_lower] - arr_v[peak_upper]) / arr_v[peak_upper] * 100, 3)
        
        ## 승률 계산
        hit_ratio = len(result_data.loc[result_data['profit_D+1'] > 0, :].index)/len(result_data.index) * 100

        print('cagr : %.2f %%' %cagr)
        print('mdd : %.2f %%' %mdd)
        print('승률 : %.2f %%' %hit_ratio)
        print('-----------------------------------------------------')
        print(result_data['profit_D+1'].describe())
        print('-----------------------------------------------------')


class get_vis_data():

    def __init__(self):



    ## 그래프 그리기
    def draw_graph(self, result_data):
        fig = go.Figure()
        
        t1 = go.Scatter(x=result_data['date'], y=result_data['total'])
        
        fig.add_traces(t1)
        
        fig.update_layout(
            title={
                'text': "%s OVERNIGHT" %self.code,
                'y':0.9,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'}, 
                xaxis_tickangle=-45
             )

        fig.show()

        return True