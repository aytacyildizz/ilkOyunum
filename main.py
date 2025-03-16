import arcade
from arcade.examples.array_backed_grid import WINDOW_WIDTH
from arcade.examples.camera_platform import TILE_SCALING, GRAVITY
from arcade.examples.minimap_texture import PLAYER_MOVEMENT_SPEED
from arcade.examples.template_platformer import PLAYER_JUMP_SPEED, COIN_SCALING
from pyglet.event import EVENT_HANDLE_STATE

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "Bıyık Adam"
TILE_SCALING = 0.5
COIN_SCALING = 0.5
PLAYER_MOVEMENT_SPEED = 5
GRAVITY = 1
PLAYER_JUMP_SPEED = 20


class InstructionView(arcade.View):

    def on_show_view(self):
        self.background_color = arcade.csscolor.DARK_SLATE_BLUE
        #başlangıç ekranı. farklı view classları ile gösterilecek.
        self.window.default_camera.use()
        self.title_text = arcade.Text(
            "BIYIK ADAM",
            x=self.window.width / 2,
            y=self.window.height / 2,
            color=arcade.color.WHITE,
            font_size=50,
            anchor_x="center",
        )
        self.instruction_text = arcade.Text(
            "BAŞLAMAK İÇİN 'ENTER'A BAS",
            x=self.window.width / 2,
            y=self.window.height / 2-75,
            color=arcade.color.WHITE,
            font_size=20,
            anchor_x="center",
        )
    def on_draw(self):
        self.clear()
        self.title_text.draw()
        self.instruction_text.draw()

    def on_key_press(self, key: int, modifiers: int) -> bool | None:
        if key == arcade.key.ENTER:
            game_view = GameView()
            game_view.setup()
            self.window.show_view(game_view)


class GameOverView(arcade.View):

    def __init__(self):
        super().__init__()
        self.window.default_camera.use()
        self.gameover_text = arcade.Text(
            "OYNADIĞINIZ İÇİN TEŞEKKÜRLER",
            x=self.window.width / 2,
            y=self.window.height / 2,
            color=arcade.color.WHITE,
            font_size=50,
            anchor_x="center",)
        self.introduction_text = arcade.Text(
            "BAŞA DÖNMEK İÇİN 'ENTER'",
            x=self.window.width / 2,
            y=self.window.height / 2-75,
            color=arcade.color.WHITE,
            font_size=30,
            anchor_x="center",)
        self.exit_text = arcade.Text(
            "ÇIKMAK İÇİN 'BOŞLUK'",
            x=self.window.width / 2,
            y=self.window.height / 2 - 125,
            color=arcade.color.WHITE,
            font_size=30,
            anchor_x="center", )
        self.background_color = arcade.csscolor.DARK_SLATE_BLUE

    def on_draw(self):
        self.clear()
        self.gameover_text.draw()
        self.introduction_text.draw()
        self.exit_text.draw()

    def on_key_press(self, key: int, modifiers: int) -> bool | None:
        if key == arcade.key.ENTER:
            game_view = GameView()
            game_view.setup()
            self.window.show_view(game_view)

        if key == arcade.key.SPACE:
            arcade.exit()

class GameView(arcade.View):

    def __init__(self):

        super().__init__()
        #default değerler.

        self.player_texture = None
        self.player_sprite = None
        self.tile_map = None
        self.scene = None
        self.camera = None
        self.gui_camera = None #skoru sabit tutmak için ikinci bir sabit kamera tanımlıyoruz.
        self.score = 0 #skor değişkeni tanımla ve on update metoduna ekle.
        self.score_text = None #burası text formatı için tanımlanan değişken.
        self.gameover_text = None
        self.end_of_map = 0
        self.level = 1
        self.level_text = None
        self.reset_score = True
        self.collect_coin_sound = arcade.load_sound(":resources:sounds/coin1.wav")
        self.jump_sound = arcade.load_sound(":resources:sounds/jump1.wav")
        #sesleri setup içine değilde init içine tanımlamamızın sebebi, oyunu sıfırlarken sesi yeniden
        #yüklemeye gerek yok çünkü sesler değişmiyor.
        self.gameover_sound = arcade.load_sound(":resources:sounds/gameover1.wav") #yanınca oynatılacak ses.

    def setup(self):

        layer_options = {"Platforms":{"use_spatial_hash":True}}
        self.tile_map = arcade.load_tilemap(
            f":resources:tiled_maps/map2_level_{self.level}.json",
            scaling=TILE_SCALING,
            layer_options=layer_options) #sonraki level'ı yüklemek için.

        self.scene = arcade.Scene.from_tilemap(self.tile_map)
        self.player_texture = arcade.load_texture(
            ":resources:images/animated_characters/male_person/malePerson_idle.png")
        # hazır bir karakter görüntüsü al.
        self.scene.add_sprite_list_after("Player", "Foreground")
        #anladığım kadarıyla buraya ilk yazılan obje, map'te tanımlı--
        #"Foreground" obje listesinin önüne çiziliyor. bu işe yaramadı, tekrar kontrol et.
        self.player_sprite = arcade.Sprite(self.player_texture)
        self.player_sprite.center_x = 128
        self.player_sprite.center_y = 128
        # bu görüntüyü bir sprite a dönüştür ve konumunu ayarla.
        #önceki denemede list kullandık ama şimdi arcade'in Scene Class'ını kullanıcaz.
        self.scene.add_sprite("player", self.player_sprite)

        self.physics_engine = arcade.PhysicsEnginePlatformer(self.player_sprite, walls=self.scene["Platforms"],
                                                                 gravity_constant=GRAVITY)
        # arcade içinde tanımlı basit fizik motorunu setup fonksiyonu içine çek.
        self.camera = arcade.camera.Camera2D() #oyuncuyu takip edecek kamera
        self.gui_camera = arcade.camera.Camera2D()  # skoru gösterecek kamera
        if self.reset_score:
            self.score = 0
        self.reset_score = True
        self.score_text = arcade.Text(f"Score: {self.score}", x=5, y=705)
        self.level_text = arcade.Text(
            f"LEVEL {self.level}",
            x=self.window.width / 2,
            y=self.window.height - 100,
            color=arcade.color.ANTIQUE_WHITE,
            anchor_x="center",
            font_size=52)
        self.background_color = arcade.csscolor.BURLYWOOD  # arka plan rengini ayarla
        self.end_of_map = (self.tile_map.width * self.tile_map.tile_width)
        self.end_of_map *= self.tile_map.scaling
        print(self.end_of_map) #tile daki pixel sayısını tile sayısı ile çarparak map'in bittiği yeri bulduk.

    def on_draw(self):
        self.clear()
        self.camera.use() #çizimlerden önce kamerayı aktif et.
        self.scene.draw()
        self.gui_camera.use()
        self.score_text.draw()
        self.level_text.draw()

    def on_update(self, delta_time: float) -> bool | None:
        self.physics_engine.update() #fizik motorunu saniyede 60 kere update edecek metod. (default)
        coin_hit_list = arcade.check_for_collision_with_list(self.player_sprite, self.scene["Coins"])
        for coin in coin_hit_list:
            coin.remove_from_sprite_lists() #oyuncu ile collision olan altınları listeye al.
            #listedeki coinleri kaldır.
            arcade.play_sound(self.collect_coin_sound) #altın toplama sesi
            self.score += 75 #her altın toplandığında score değişkenini arttır.
            self.score_text.text = f"Score: {self.score}"

        if arcade.check_for_collision_with_list(self.player_sprite, self.scene["Don't Touch"]):
            # "Don't Touch" ----> Lav katmanı
            arcade.play_sound(self.gameover_sound)
            self.setup() #lava değdiğinde sesi çal ve setup'ı başa sar.

        if self.player_sprite.center_x >= self.end_of_map: #oyuncu haritanın sonuna geldimi kontrol et.
            self.level += 1 #harita sonuna geldiyse üst levele ata
            if self.level >= 3:
                view = GameOverView()
                self.window.show_view(view)
            else:
                self.reset_score = False
                self.setup()

        self.camera.position = self.player_sprite.position

        if self.player_sprite.center_y <= 0:
            self.reset_score = True
            arcade.play_sound(self.gameover_sound)
            self.setup()

    def on_key_press(self, key: int, modifiers: int) -> EVENT_HANDLE_STATE:
        if key == arcade.key.ESCAPE:
            self.setup() #escape basıldığında setup fonksiyonun çağır. (oyunu sıfırlar)
        #ok tuşları veya "wasd" basıldığında çağırılacak metod.
        if key == arcade.key.UP or key == arcade.key.W:
            if self.physics_engine.can_jump(): #can_jump, havadayken zıplamayı etkisiz bırakıyor.
                self.player_sprite.change_y = PLAYER_JUMP_SPEED
                arcade.play_sound(self.jump_sound) #zıplama sesi
        if key == arcade.key.LEFT or key == arcade.key.A:
            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED

    def on_key_release(self, key: int, modifiers: int) -> EVENT_HANDLE_STATE:
        #tuşlara basmayı bıraktığımızda çağırılacak metod.
        if key == arcade.key.LEFT or key == arcade.key.A:
            self.player_sprite.change_x = 0
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.player_sprite.change_x = 0 #tuş bırakıldığında hareketi sıfırla.


def main():
    window = arcade.Window(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)
    start_view = InstructionView()
    window.show_view(start_view)
    arcade.run()

if __name__ == "__main__":
    main()
