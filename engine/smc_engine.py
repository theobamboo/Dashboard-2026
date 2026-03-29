import pandas as pd

class SMCEngine:
    def __init__(self):
        pass

    def detect_structures(self, df):
        """
        Detects FVGs and BOS from a dataframe with an 'open', 'high', 'low', 'close' column.
        Returns a dictionary with lists of FVGs and BOS for plotting.
        """
        if df.empty or not all(col in df.columns for col in ['open', 'high', 'low', 'close']):
            return {'fvgs': [], 'bos': []}
            
        fvgs = []
        bos_lines = []
        
        # 1. Detect FVGs (Fair Value Gaps)
        for i in range(2, len(df)):
            c1_high = df['high'].iloc[i-2]
            c1_low  = df['low'].iloc[i-2]
            c3_high = df['high'].iloc[i]
            c3_low  = df['low'].iloc[i]
            
            c2_time = df.index[i-1]
            end_time = df.index[-1]
            
            # Bullish FVG
            if c3_low > c1_high:
                fvgs.append({
                    'type': 'bullish',
                    'top': c3_low,
                    'bottom': c1_high,
                    'start_time': c2_time,
                    'end_time': end_time
                })
            # Bearish FVG
            elif c3_high < c1_low:
                fvgs.append({
                    'type': 'bearish',
                    'top': c1_low,
                    'bottom': c3_high,
                    'start_time': c2_time,
                    'end_time': end_time
                })

        # 2. Detect BOS (Break of Structure)
        N = 3
        swing_highs = []
        swing_lows = []
        
        for i in range(N, len(df) - N):
            is_swing_high = True
            is_swing_low = True
            for j in range(1, N+1):
                if df['high'].iloc[i] <= df['high'].iloc[i-j] or df['high'].iloc[i] <= df['high'].iloc[i+j]:
                    is_swing_high = False
                if df['low'].iloc[i] >= df['low'].iloc[i-j] or df['low'].iloc[i] >= df['low'].iloc[i+j]:
                    is_swing_low = False
                    
            if is_swing_high:
                swing_highs.append({'price': df['high'].iloc[i], 'time': df.index[i]})
            if is_swing_low:
                swing_lows.append({'price': df['low'].iloc[i], 'time': df.index[i]})
                
        # Detect breaches of recent swing levels
        active_highs = []
        for idx in range(len(df)):
            current_time = df.index[idx]
            current_close = df['close'].iloc[idx]
            
            # Add new swing high
            sw_h = [h for h in swing_highs if h['time'] == current_time]
            if sw_h:
                active_highs.append({'price': sw_h[0]['price'], 'start_time': current_time, 'broken': False, 'type': 'bullish'})
                
            # Check for breach
            for aw in active_highs:
                if not aw['broken'] and current_close > aw['price']:
                    aw['broken'] = True
                    bos_lines.append({
                        'type': 'bullish',
                        'price': aw['price'],
                        'start_time': aw['start_time'],
                        'end_time': current_time
                    })
            active_highs = [aw for aw in active_highs if not aw['broken']]
             
        active_lows = []
        for idx in range(len(df)):
            current_time = df.index[idx]
            current_close = df['close'].iloc[idx]
            
            # Add new swing low
            sw_l = [l for l in swing_lows if l['time'] == current_time]
            if sw_l:
                active_lows.append({'price': sw_l[0]['price'], 'start_time': current_time, 'broken': False, 'type': 'bearish'})
                
            # Check for breach
            for al in active_lows:
                if not al['broken'] and current_close < al['price']:
                    al['broken'] = True
                    bos_lines.append({
                        'type': 'bearish',
                        'price': al['price'],
                        'start_time': al['start_time'],
                        'end_time': current_time
                    })
            active_lows = [al for al in active_lows if not al['broken']]
            
        return {
            'fvgs': fvgs[-15:], # Keep the 15 most recent
            'bos': bos_lines[-15:] # Keep the 15 most recent
        }
