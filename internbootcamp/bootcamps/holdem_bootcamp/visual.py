import os
from PIL import Image, ImageDraw, ImageFont


class PokerTableDrawer:
    def __init__(self, width=1200, height=800, card_folder="./cards", filename=""):
        self.width = width
        self.height = height
        self.card_folder = card_folder
        self.filename = filename
        
        # --- 颜色配置 ---
        self.bg_color = (20, 20, 20)
        self.table_color = (34, 100, 50)
        self.text_color = (255, 255, 255)
        
        # 按钮颜色方案
        self.btn_colors = {
            'fold': {'bg': (80, 80, 80), 'border': (40, 40, 40)},     # 灰
            'check': {'bg': (40, 160, 80), 'border': (20, 100, 40)},  # 绿
            'call': {'bg': (40, 100, 180), 'border': (20, 60, 120)},  # 蓝
            'bet': {'bg': (40, 100, 180), 'border': (20, 60, 120)},   # 蓝
            'raise': {'bg': (40, 100, 180), 'border': (20, 60, 120)}, # 蓝
            'allin': {'bg': (220, 40, 40), 'border': (160, 20, 20)},  # 红
        }

        self.card_aspect_ratio = 1.4 
        
        # --- 自适应计算 ---
        self.scale = min(width / 1200, height / 800)
        self.cx = width // 2
        self.cy = height // 2
        
        # 区域位置
        self.pos_villain_y = int(height * 0.15)
        self.pos_hero_y = int(height * 0.85)
        self.pos_board_y = int(height * 0.45)
        
        # 尺寸定义
        self.card_width_std = int(100 * self.scale) 
        self.avatar_size = int(100 * self.scale)
        self.info_panel_w = int(160 * self.scale)
        self.info_panel_h = int(60 * self.scale)
        
        # 字体加载
        self.font_large = self._get_font(int(40 * self.scale))
        self.font_medium = self._get_font(int(24 * self.scale))
        self.font_small = self._get_font(int(16 * self.scale))
        self.font_btn = self._get_font(int(15 * self.scale)) # 按钮字体

    def _get_font(self, size):
        try:
            return ImageFont.truetype("arial.ttf", size)
        except OSError:
            try:
                return ImageFont.truetype("DejaVuSans.ttf", size)
            except OSError:
                return ImageFont.load_default()
            
    def _trim_transparent_borders(self, img):
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        alpha = img.getchannel('A')
        bbox = alpha.getbbox()
        if bbox:
            return img.crop(bbox)
        return img

    def _load_image(self, path, target_width=None, force_ratio=None):
        if not os.path.exists(path):
            return None
        try:
            img = Image.open(path).convert("RGBA")
            img = self._trim_transparent_borders(img)
            if target_width:
                if force_ratio:
                    target_height = int(target_width * force_ratio)
                    img = img.resize((target_width, target_height), Image.Resampling.LANCZOS)
                else:
                    aspect_ratio = img.height / img.width
                    new_height = int(target_width * aspect_ratio)
                    img = img.resize((target_width, new_height), Image.Resampling.LANCZOS)
            return img
        except Exception as e:
            print(f"Error loading {path}: {e}")
            return None

    def get_card_path(self, card_code):
        if not card_code:
            return os.path.join(self.card_folder, "back.png")
        return os.path.join(self.card_folder, f"{card_code.lower()}.png")

    def draw_table_background(self):
        bg_path = "table_bg.png"
        if os.path.exists(bg_path):
            return self._load_image(bg_path, self.width).convert("RGBA"), None
        
        img = Image.new('RGBA', (self.width, self.height), self.bg_color)
        draw = ImageDraw.Draw(img)
        
        margin_x = int(self.width * 0.08)
        margin_y = int(self.height * 0.15)
        bbox = [margin_x, margin_y, self.width - margin_x, self.height - margin_y]
        
        border_width = int(20 * self.scale)
        draw.ellipse([b - border_width if i < 2 else b + border_width for i, b in enumerate(bbox)], fill=(10, 10, 10))
        draw.ellipse(bbox, fill=self.table_color)
        return img, draw

    def draw_hand(self, img, cards, center_x, center_y, card_width, spacing=None):
        if not cards: return
        if spacing is None: spacing = int(card_width * 0.1)

        total_width = len(cards) * card_width + (len(cards) - 1) * spacing
        start_x = center_x - total_width // 2
        card_height = int(card_width * self.card_aspect_ratio)
        
        for i, card_code in enumerate(cards):
            path = self.get_card_path(card_code)
            card_img = self._load_image(path, target_width=card_width, force_ratio=self.card_aspect_ratio)
            
            x = int(start_x + i * (card_width + spacing))
            y = int(center_y)
            
            if card_img:
                shadow_offset = int(4 * self.scale)
                shadow = Image.new("RGBA", card_img.size, (0, 0, 0, 80))
                img.paste(shadow, (x + shadow_offset, y + shadow_offset), shadow)
                img.paste(card_img, (x, y), card_img)
            else:
                draw = ImageDraw.Draw(img)
                draw.rectangle([x, y, x + card_width, y + card_height], outline="red", width=2)
                draw.text((x + 5, y + 5), card_code or "?", fill="red", font=self.font_small)

    def draw_player(self, img, x, y, info, is_hero=False, avatar_path=None):
        draw = ImageDraw.Draw(img)
        avatar_r = self.avatar_size // 2
        avatar_x = x - avatar_r
        avatar_y = y - avatar_r
        
        loaded_avatar = self._load_image(avatar_path, target_width=self.avatar_size) if avatar_path else None
        
        if loaded_avatar:
            mask = Image.new("L", (self.avatar_size, self.avatar_size), 0)
            ImageDraw.Draw(mask).ellipse((0, 0, self.avatar_size, self.avatar_size), fill=255)
            if loaded_avatar.size != (self.avatar_size, self.avatar_size):
                 loaded_avatar = loaded_avatar.resize((self.avatar_size, self.avatar_size))
            img.paste(loaded_avatar, (int(avatar_x), int(avatar_y)), mask)
            draw.ellipse([avatar_x, avatar_y, avatar_x+self.avatar_size, avatar_y+self.avatar_size], outline="#ccc", width=3)
        else:
            color = (50, 100, 200) if is_hero else (200, 60, 60)
            draw.ellipse([avatar_x, avatar_y, avatar_x+self.avatar_size, avatar_y+self.avatar_size], fill=color, outline="white", width=2)
            initial = info['name'][0].upper() if info['name'] else "?"
            draw.text((x, y), initial, font=self.font_large, fill="white", anchor="mm")

        if info.get('is_dealer'):
            d_radius = int(15 * self.scale)
            d_x = x + avatar_r
            d_y = y + avatar_r - int(30 * self.scale)
            draw.ellipse([d_x, d_y, d_x + d_radius*2, d_y + d_radius*2], fill="white", outline="black")
            draw.text((d_x + d_radius, d_y + d_radius), "D", fill="black", font=self.font_small, anchor="mm")

        panel_gap = int(5 * self.scale)
        panel_x = x - self.info_panel_w // 2
        panel_y = y + avatar_r + panel_gap
        
        overlay = Image.new('RGBA', img.size, (0,0,0,0))
        ImageDraw.Draw(overlay).rounded_rectangle(
            [panel_x, panel_y, panel_x + self.info_panel_w, panel_y + self.info_panel_h], 
            radius=int(10*self.scale), fill=(0, 0, 0, 180)
        )
        img.alpha_composite(overlay)
        draw = ImageDraw.Draw(img)
        
        draw.text((x, panel_y + self.info_panel_h * 0.3), info['name'], font=self.font_medium, fill="white", anchor="mm")
        draw.text((x, panel_y + self.info_panel_h * 0.75), f"${info['stack']:,}", font=self.font_medium, fill="#4ade80", anchor="mm")

        bet_gap = int(20 * self.scale)
        if not is_hero:
            panel_bottom = panel_y + self.info_panel_h
            bet_y = panel_bottom + bet_gap
        else:
            avatar_top = y - avatar_r
            bet_y = avatar_top - bet_gap

        chip_r = int(12 * self.scale)
        draw.ellipse([x-chip_r, bet_y-chip_r, x+chip_r, bet_y+chip_r], fill="orange", outline="white")
        text_x = x + int(20 * self.scale)
        draw.text((text_x, bet_y), f"{info['bet']:,}", font=self.font_medium, fill="gold", anchor="lm")

    # --- 绘制行动 ---
    def draw_villain_speech_bubble(self, img, x, y, action_text, is_hero):
        if not action_text: 
            return
        
        draw = ImageDraw.Draw(img)
        
        # 气泡配置
        bubble_bg = (255, 255, 255)      # 白底
        bubble_outline = None  # (200, 200, 200) # 浅灰边框
        text_fill = (30, 30, 30)         # 深色文字
        
        # 计算文字大小
        bbox = draw.textbbox((0, 0), action_text, font=self.font_medium)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        
        padding_x = int(10 * self.scale)
        padding_y = int(15 * self.scale)
        bubble_w = text_w + padding_x * 2
        bubble_h = text_h + padding_y * 2
        
        # x, y 是头像中心点
        avatar_r = self.avatar_size // 2
        
        # 气泡尖角相对于头像中心的偏移量
        # 如果在左边，尖角起点的 X 应该是负的
        offset_x_dist = avatar_r + int(5 * self.scale)
        offset_x = offset_x_dist if is_hero else -offset_x_dist
        offset_y = -int(10 * self.scale) 
        
        # 计算气泡矩形左上角坐标 (rect_x, rect_y)
        tail_length = int(20 * self.scale) # 尾巴横向长度
        
        if is_hero:
            # 右侧逻辑 (原逻辑)：
            # rect_x = 头像中心 + 尖角偏移(正数) + 尾巴长度
            rect_x = x + offset_x + tail_length
        else:
            # 左侧逻辑：
            # rect_x = 头像中心 + 尖角偏移(负数) - 尾巴长度 - 气泡宽度
            rect_x = x + offset_x - tail_length - bubble_w

        # Y轴逻辑不变，气泡向上飘
        rect_y = y + offset_y - bubble_h
        
        # 1. 绘制气泡主体（圆角矩形）
        draw.rounded_rectangle(
            [rect_x, rect_y, rect_x + bubble_w, rect_y + bubble_h],
            radius=int(10 * self.scale),
            fill=bubble_bg,
            outline=bubble_outline,
            width=2
        )
        
        # 2. 绘制气泡的小尾巴（三角形指向头像）
        tail_tip = (x + offset_x, y + offset_y)
        
        # 计算尾巴在气泡上的基座位置
        # 垂直方向位置不变
        base_y_top = rect_y + bubble_h // 2 - int(5 * self.scale)
        base_y_bottom = rect_y + bubble_h // 2 + int(15 * self.scale)
        
        if is_hero:
            # 右侧：基座在气泡的左边缘 (rect_x)
            base_x = rect_x
        else:
            # 左侧：基座在气泡的右边缘 (rect_x + bubble_w)
            base_x = rect_x + bubble_w
            
        tail_base_top = (base_x, base_y_top)
        tail_base_bottom = (base_x, base_y_bottom)
        
        draw.polygon([tail_tip, tail_base_top, tail_base_bottom], fill=bubble_bg)
        
        # 勾勒尾巴边缘
        draw.line([tail_tip, tail_base_top], fill=bubble_outline, width=2)
        draw.line([tail_tip, tail_base_bottom], fill=bubble_outline, width=2)
        
        # 3. 绘制文字 (位置计算不变，基于 rect_x 自动适应)
        center_x = rect_x + bubble_w / 2
        center_y = rect_y + bubble_h / 2
        
        draw.text(
            (center_x, center_y), 
            action_text, 
            font=self.font_medium, 
            fill=text_fill, 
            anchor="mm" 
        )

    # --- 绘制右下角 Hero 按钮 ---
    def draw_hero_buttons(self, img, actions):
        if not actions: return
        
        draw = ImageDraw.Draw(img)
        
        # 按钮参数
        btn_width = int(100 * self.scale)
        btn_height = int(50 * self.scale)
        spacing = int(15 * self.scale)
        margin_bottom = int(30 * self.scale)
        margin_right = int(30 * self.scale)
        
        # 从右向左绘制
        current_x = self.width - margin_right - btn_width
        y = self.height - margin_bottom - btn_height
        
        # 倒序遍历，保证第一个动作在最右边（或者按你的习惯顺序）
        # 这里假设 actions 列表顺序为 ['Fold', 'Call', 'Raise']，我们希望 Raise 在最右边，Fold 在最左边
        # 所以我们从右往左画，先画列表最后一个
        
        for action_text in reversed(actions):
            # 确定颜色
            key = action_text.lower().split()[0] # 取第一个词判断类型 (e.g. "Raise 200" -> "raise")
            colors = self.btn_colors[key]
            
            # 绘制按钮背景
            draw.rounded_rectangle(
                [current_x, y, current_x + btn_width, y + btn_height],
                radius=int(8*self.scale),
                fill=colors['bg'],
                outline=colors['border'],
                width=2
            )
            
            # 绘制文字 (居中)
            text_x = current_x + btn_width / 2
            text_y = y + btn_height / 2
            draw.text((text_x, text_y), action_text, font=self.font_btn, fill="white", anchor="mm")
            
            # 更新 X 坐标，向左移动
            current_x -= (btn_width + spacing)

    def draw_game_info(self, img, game_info):
        """
        绘制左上角的游戏信息面板
        info_data: dict, 例如 {'Blinds': '100/200', 'Ante': '0', 'Street': 'Flop'}
        """
        draw = ImageDraw.Draw(img)
        
        # --- 样式配置 ---
        margin_x = int(20 * self.scale)  # 距离左边缘
        margin_y = int(20 * self.scale)  # 距离上边缘
        padding = int(15 * self.scale)   # 文字与框的内边距
        line_height = int(25 * self.scale) # 行高

        # --- 计算面板尺寸 ---
        max_text_width = 0

        bbox = draw.textbbox((0, 0), game_info, font=self.font_small)
        max_text_width = bbox[2] - bbox[0]
        
        panel_w = max_text_width + padding * 2
        panel_h = line_height + padding * 2
        
        # --- 绘制半透明背景 ---
        # 创建一个专门用于半透明图层的图像
        overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        
        overlay_draw.rounded_rectangle(
            [margin_x, margin_y, margin_x + panel_w, margin_y + panel_h],
            radius=int(10 * self.scale),
            fill=(255, 255, 255),  # 白底
            width=1
        )
        
        # 将半透明层合并到底图
        img.alpha_composite(overlay)
        
        # --- 绘制文字 ---
        # 重新获取 draw 对象（因为 alpha_composite 可能改变了状态，虽然通常不需要，但保险起见）
        draw = ImageDraw.Draw(img)
        
        # 文字垂直居中修正
        draw.text(
            (margin_x + padding, margin_y + padding), 
            game_info, 
            font=self.font_small, 
            fill=(0, 0, 0) # 浅灰色文字
        )

    def generate(self, hero_data, villain_data, board_cards, pot_size, game_info=""):
        img, draw = self.draw_table_background()
        if draw is None: draw = ImageDraw.Draw(img)

        # 绘制左上角信息框
        if game_info:
            self.draw_game_info(img, game_info)
        
        # 1. 绘制公共牌
        if board_cards:
            self.draw_hand(img, board_cards, self.cx, self.pos_board_y, 
                           card_width=self.card_width_std, spacing=int(10*self.scale))
        
        # 2. 绘制底池
        padding = int(20 * self.scale)
        pot_y = self.pos_board_y - padding
        draw.text((self.cx, pot_y), f"Total Pot: {pot_size:,}", font=self.font_medium, fill="#ffd700", anchor="mb") 

        card_height = int(self.card_width_std * self.card_aspect_ratio)
        card_spacing = int(5 * self.scale)
        
        def get_hand_layout_params(cards):
            num = len(cards) if cards else 2
            total_hand_w = num * self.card_width_std + (num - 1) * card_spacing
            offset_x = (self.avatar_size // 2) + int(20 * self.scale) + (total_hand_w)
            start_y = - (card_height // 2)
            return offset_x, start_y

        # 3. 绘制对手 (上方)
        v_cards = villain_data.get('cards')
        if v_cards is None: v_cards = [None, None]
        self.draw_player(img, self.cx, self.pos_villain_y, villain_data, is_hero=False, avatar_path=villain_data.get('avatar'))
        v_offset_x, v_offset_y = get_hand_layout_params(v_cards)
        self.draw_hand(img, v_cards, self.cx + v_offset_x, self.pos_villain_y + v_offset_y, card_width=self.card_width_std, spacing=card_spacing)

        # --- 绘制对手上一轮行动 (左上角) ---
        # 假设 villain_data 中有一个 'action' 字段表示上一轮动作
        villain_action = villain_data.get('action') 
        if villain_action:
            self.draw_villain_speech_bubble(img, self.cx, self.pos_villain_y, villain_action, is_hero=False)

        # 4. 绘制自己 (下方)
        h_cards = hero_data.get('cards', [])
        self.draw_player(img, self.cx, self.pos_hero_y, hero_data, is_hero=True, avatar_path=hero_data.get('avatar'))
        h_offset_x, h_offset_y = get_hand_layout_params(h_cards)
        self.draw_hand(img, h_cards, self.cx - h_offset_x, self.pos_hero_y + h_offset_y, card_width=self.card_width_std, spacing=card_spacing)

        # --- 绘制 Hero 可用动作按钮 (右下角) ---
        hero_action = hero_data.get('action') 
        if hero_action:
            self.draw_villain_speech_bubble(img, self.cx, self.pos_hero_y, hero_action, is_hero=True)
        else:
            hero_choices = hero_data.get('choices', [])
            self.draw_hero_buttons(img, hero_choices)

        img.convert("RGB").save(self.filename)

# ==========================================
# 调用示例
# ==========================================
if __name__ == "__main__":
    drawer = PokerTableDrawer(filename="poker_result.png")

    # 模拟数据输入
    hero_info = {
        'name': 'You',
        'stack': 101000,
        'bet': 100,
        'cards': ['Ah', 'Kh'],
        'avatar': 'avatars/hero.png',
        'is_dealer': True,
        'choices': ['Fold', 'Check', 'Bet 200', 'AllIn'],
        'action': 'Check'  
    }

    villain_info = {
        'name': 'Player',
        'stack': 16420,
        'bet': 0,
        'cards': [None, None],
        'avatar': 'avatars/villain.png',
        'is_dealer': False,
        'action': 'Check' 
    }

    board = ['2d', 'Kc', 'Ac', '6s', None]
    pot = 114000

    drawer.generate(hero_info, villain_info, board, pot)
