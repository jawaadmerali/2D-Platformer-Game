import pygame
import Level as Lvl
#initialization of mixer module 
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.mixer.init()
pygame.init()

"""
Setup
-where we'll include game settings
"""
worldx = 544 #change window size to fit tiles
worldy = 544
FPS   = 40  # frame rate
ani   = 4   # animation cycles
clock = pygame.time.Clock()
world = pygame.display.set_mode([worldx,worldy])
main_menu = True 

#load backdrop image--> extension from lesson 5
sky = pygame.image.load('Assets/sky.png')
background = pygame.transform.scale(sky, (worldx,worldy))
restart = pygame.image.load('Assets/restart.png')
restart_img = pygame.transform.scale(restart, (125,50))
start = pygame.image.load('Assets/start.png')
start_img = pygame.transform.scale(start, (188,75))
exit = pygame.image.load('Assets/exit.png')
exit_img = pygame.transform.scale(exit, (188,75))

#load sound files 
jump_fx = pygame.mixer.Sound('Assets/jump.wav')
jump_fx.set_volume(0.5)
treasure_fx = pygame.mixer.Sound('Assets/treasure.wav')
treasure_fx.set_volume(0.8)
injury_fx = pygame.mixer.Sound('Assets/injury.wav')
injury_fx.set_volume(0.9)

BLUE  = (25, 25, 200)
BLACK = (23, 23, 23)
WHITE = (254, 254, 254)
RED = (200, 25, 25) #<--customize extra game colors
GREEN = (25, 200, 25)
play_game = True
pygame.display.set_caption('My Game World')
steps = 5 # how many pixels to move
tile_size = 32 #adjust tile size 
level_map = [Lvl.tile_map_1, Lvl.tile_map_2]
move_left = False
move_right = False
move_up = False
move_down = False

#imaginary scroll boundary walls
backwardx_wall = 100 #left side imaginary wall
forwardx_wall = worldx - 100 #right side imaginary wall

#sprite groups 
player_list = pygame.sprite.Group()
main_group = pygame.sprite.Group() #all tiles 
plat_list = pygame.sprite.Group()#platform tiles the player can stand on
danger_tile_list = pygame.sprite.Group() 
enemy_list = pygame.sprite.Group()
portal_list = pygame.sprite.Group() 
ruby_tiles = pygame.sprite.Group() 

"""
Objects
-the code to make characters in our game
"""
#Button class with coordinates and image as parameters
#load button images underneath background images
class Button():
  def __init__(self, x, y, image):
    self.image = image
    self.rect = self.image.get_rect()
    self.rect.x = x
    self.rect.y = y

  def create(self):
    #variable that reports whether you've clicked the button 
    action = False

    #get mouse position 
    position = pygame.mouse.get_pos()
    #check mouse over button & click conditions
    if self.rect.collidepoint(position):
      #print('Mouse over button. ') #just to see if it works
      
      #left mouse click
      if pygame.mouse.get_pressed()[0] == 1 and self.clicked ==False:
        #print('Clicked! ')
        action = True
        self.clicked = True
      #left click released
      if pygame.mouse.get_pressed()[0] == 0:
        self.clicked = False 

    #draw button 
    world.blit(self.image, self.rect)

    return action 


    
#make a game glass
class Game():
  def __init__(self, player, enemy_list, danger_tile_list, portal_list, ruby_tiles):
    self.player = player
    self.enemy_list = enemy_list
    self.danger_tile_list = danger_tile_list
    self.portal_list = portal_list
    self.ruby_tiles = ruby_tiles
    self.lvl_counter = 0
    self.lives = 3
    self.score = 0 
    self.HUD_font = pygame.font.Font(None, 24)
    self.gameover = False
    create_world(level_map[0])
    self.travel_x = 0


  def draw(self):
    WHITE = (255, 255, 255)
    lives_text = self.HUD_font.render('Lives: ' + str(self.lives), True, WHITE)
    lives_rect = lives_text.get_rect()
    lives_rect.topleft = (10,10)
    score_text = self.HUD_font.render('Score: ' + str(self.score) + '/ 5', True, WHITE)
    score_rect = score_text.get_rect()
    score_rect.topleft = (worldx - 100,10)

    world.blit(lives_text, lives_rect)
    world.blit (score_text, score_rect)


    if self.gameover == True:
      player.image = player.wings
      player.rect.x = worldx/2 - 80
      if player.rect.y > 150:
        player.travel_y = -8
      else:
        player.rect.y = 150
        player.travel_y -= 3
    
      #print('game over')
      if restart_button.create():
        #print('restart')
        #reset variables
        player.kill()
        enemy.kill()
        for tile in main_group:
          tile.kill()
        self.lives = 3
        self.score = 0
        self.gameover = False
        create_world(level_map[0])

  #level advancement
  def level_finish(self):
    portal_collision = pygame.sprite.spritecollide(player, portal_list, False)
    for portal in portal_collision:
      if self.score == 5:
        self.level_progress()

  def level_progress(self):
    player.kill()
    enemy.kill()
    for tile in main_group:
      tile.kill()
    self.lvl_counter += 1
    create_world(level_map[self.lvl_counter])
    player.move(steps,0)
    self.score = 0

  #check lives method
  def check_lives(self):
    enemy_collide = pygame.sprite.spritecollide(player, enemy_list, False)
    for enemy in enemy_collide:
      injury_fx.play()
      player.is_colliding = False
      player.attacked = True
      self.lives -= 1
      player.rect.bottom = enemy.rect.top +1
      player.travel_y = -33
   
     

    danger_collide = pygame.sprite.spritecollide(player, danger_tile_list, False)
    for danger in danger_collide:
      injury_fx.play()
      player.attacked = True
      player.is_colliding = False
      self.lives -= 1
      player.rect.bottom = danger.rect.top +1
      player.travel_y = -33
      
    #gameover conditions
  def check_go(self):
    if self.lives <= 0:
      self.gameover = True

  #check_loot_collisions
  def check_collisions(self):
    ruby_collision = pygame.sprite.spritecollide(player, ruby_tiles, True)
    for ruby in ruby_collision:
      treasure_fx.play()
      self.score += 1
          
class Player(pygame.sprite.Sprite):
  def __init__(self, x, y):
    super().__init__()
    player_pic = pygame.image.load('Assets/player.png')
    #self.image = pygame.Surface([self.width, self.height])
    #self.image.fill(GREEN)
    sparking_pic = pygame.image.load('Assets/sparking_robot.png')
    wings_pic = pygame.image.load('Assets/Robot_wings.png')
    damaged_pic = pygame.image.load('Assets/damaged.png')
    self.damaged_image = pygame.transform.scale(damaged_pic, (tile_size, tile_size))
    self.image = pygame.transform.scale(player_pic, (tile_size, tile_size))
    self.wings = pygame.transform.scale(wings_pic, (5*tile_size, 4*tile_size))
    self.sparking_robot = pygame.transform.scale(sparking_pic, (3.4*tile_size,2.5*tile_size))
    self.rect = self.image.get_rect()
    self.rect.x = x  #go to x
    self.rect.y = y  #go to y
    self.travel_x = 0 # travel along X
    self.travel_y = 0 # trravel along Y
    #add a collision detection variable
    self.is_colliding = False
    self.attacked_timer = 0
    self.attacked = False
    

  def move(self, x, y):  # control player movement
    self.travel_x += x
    self.travel_y += y

  def update(self):   # update player position
    self.rect.x += self.travel_x
    self.rect.y += self.travel_y
   
    #Create a platform collision detector for y movement
    plat_collide = pygame.sprite.spritecollide(self, 
    plat_list, False)
    #vertical collisions
    for plat in plat_collide:
      if self.travel_y > 0:
        self.travel_y = 0
        self.rect.bottom = plat.rect.top 
      elif self.travel_y < 0:
        self.rect.top = plat.rect.bottom
        self.travel_y = 0
      self.is_colliding = True

    if self.attacked == True and my_game.lives > 0:
      if 0 <= self.attacked_timer <= 15:
        player.image = player.sparking_robot
      else:
        player.image = player.damaged_image
        self.attacked_timer = 0
        self.attacked = False
      
      self.attacked_timer += 1
      
    #horizontal collisions
    for plat in plat_list:
      if plat.rect.colliderect(self.rect.x - steps, self.rect.y, self.rect.width, self.rect.height):
        if self.travel_x < 0:
          self.rect.left = plat.rect.right + steps 

      elif plat.rect.colliderect(self.rect.x + steps, self.rect.y, self.rect.width, self.rect.height): 
        if self.travel_x > 0:
          self.rect.right = plat.rect.left - steps
        
  def gravity(self): #player gravity 
    if self.rect.y > worldy and self.travel_y > 0:
      self.travel_y = 0
      self.rect.y = worldy - self.rect.height
    else:
      self.travel_y += 3 
    #Add a jump method to the player class
  def jump(self):
    if self.is_colliding:
      self.travel_y -= 33  # how high to jump
      self.is_colliding = False
    
  

class Platform(pygame.sprite.Sprite):
  def __init__(self, x, y, main_group, sub_group, image_int):
    super().__init__()
    #load images
    if image_int == 1:
      grass_pic = pygame.image.load('Assets/grass.png')
      self.image = pygame.transform.scale(grass_pic, (tile_size, tile_size))
      sub_group.add(self)
    elif image_int == 2:
      water_pic = pygame.image.load('Assets/water.png')
      self.image = pygame.transform.scale(water_pic, (tile_size, tile_size))
      sub_group.add(self)
    elif image_int == 3:
      box_pic = pygame.image.load('Assets/box.png')
      self.image = pygame.transform.scale(box_pic, (tile_size, tile_size))
      sub_group.add(self)
    #portal
    elif image_int == 6:
      portal_pic = pygame.image.load('Assets/portal.png')
      self.image = pygame.transform.scale(portal_pic, (2*tile_size, 4*tile_size))
      sub_group.add(self)

    #ruby tiles
    elif image_int == 7:
      ruby_pic = pygame.image.load('Assets/ruby.png')
      self.image = pygame.transform.scale(ruby_pic, (tile_size, tile_size))
      sub_group.add(self)
    
    self.rect = self.image.get_rect()
    self.rect.y = y
    self.rect.x = x
    main_group.add(self)

#create enemy class
class Enemy(pygame.sprite.Sprite):
  def __init__(self, x, y, image_int):
    super().__init__()
    if image_int == 5:
      evil_blob = pygame.image.load('Assets/bad_slime.png')
      self.image = pygame.transform.scale(evil_blob, (tile_size, tile_size))
    #load more enemy pics later
  
    self.rect = self.image.get_rect() # Set a reference to the image rect
    self.rect.x = x 
    self.rect.y = y 
    
    #Track distance traveled by enemy
    self.travel_x = 0 # travel along X
    self.travel_y = 0 # travel along Y
    #add a collision detection variable
    self.is_colliding = False
    enemy_list.add(self)
    #add variable to keep track of how many steps enemy moves
    self.enemySteps = 0


  #update enemy position
  def update(self):
    self.rect.x += self.travel_x
    self.rect.y += self.travel_y
    distance = 100
    speed = 4

    if 0 <= self.enemySteps <= distance/2:
      self.travel_x = speed
    elif distance/2 <= self.enemySteps < distance:
      self.travel_x = -speed
    else:
      self.enemySteps = 0

    self.enemySteps += 1

    
    #Create a platform collision detector
    plat_collide = pygame.sprite.spritecollide(self, 
    plat_list, False)
    #vertical collisions
    for plat in plat_collide:
      if self.travel_y > 0:
        self.travel_y = 0
        self.rect.bottom = plat.rect.top 
    #can remove this chunk  
    #  elif self.travel_y < 0:
    #    self.rect.top = plat.rect.bottom
    #    self.travel_y = 0
    #  self.is_colliding = True
   
      
    #horizontal collisions moving left
    for plat in plat_list:
      if plat.rect.colliderect(self.rect.x - speed, self.rect.y, self.rect.width, self.rect.height):
        if self.travel_x < 0:
          self.rect.left = plat.rect.right + speed
          self.enemySteps = 0
       
    #horizontal collisions moving right      
      elif plat.rect.colliderect(self.rect.x + speed, self.rect.y, self.rect.width, self.rect.height): 
        if self.travel_x > 0:
          self.rect.right = plat.rect.left - speed
          self.enemySteps = 1 + distance/2

  #Track new ENEMY position on the y-axis to show gravity effect
    self.rect.y += self.travel_y
    
  #enemy gravity code 
    if self.rect.y > worldy and self.travel_y > 0:
      self.travel_y = 0
      self.rect.y = worldy - self.rect.height
    else:
      self.travel_y += 3
      
#make func to create Platform objects (tiles) from tile map
def create_world(level_map):
  #loop through 17 lists (moves us down)
  for row in range(len(level_map)):
    #loop through each element in given list 
    for col in range(len(level_map[row])):
      if level_map[row][col] == 1: #grass
        Platform(col*tile_size,row*tile_size,main_group, plat_list,1)
      elif level_map[row][col] == 2: #water
        Platform(col*tile_size,row*tile_size,main_group,danger_tile_list,2)
      elif level_map[row][col] == 3: #box
        Platform(col*tile_size,row*tile_size,main_group,plat_list,3)

      elif level_map[row][col] == 6: #portal
        Platform(col*tile_size,row*tile_size,main_group, portal_list, 6)

      elif level_map[row][col] == 7: #ruby
        Platform(col*tile_size,row*tile_size,main_group, ruby_tiles, 7)
        
      elif level_map[row][col] == 4: #player sprite
        global player
        player = Player(col*tile_size,row*tile_size)
        player_list.add(player)
        
      elif level_map[row][col] == 5: #enemy blob
        Enemy(col*tile_size,row*tile_size, 5)
         


create_world(level_map)

my_game = Game(player_list, enemy_list, danger_tile_list, portal_list, ruby_tiles)

#create buttons
restart_button = Button(worldx/2, worldy/2, restart_img)
start_button = Button(worldx/2 - 225, worldy/2, start_img)
exit_button = Button(worldx/2 + 40, worldy/2, exit_img)

"""
Main Loop
-keeps game running
-updates changes to state of the game, 
-displays those changes on the game screen
"""

while play_game:
  world.blit(background, (0,0))
  main_group.draw(world)
  #restart_button.create()
  if main_menu ==True: 
    if exit_button.create():
      play_game = False 
    if start_button.create():
      main_menu = False 
  
  
  else:
    #update and draw the game
    my_game.check_go()
    my_game.check_lives()
    my_game.draw()
    my_game.level_finish()
    my_game.check_collisions()
    
        # scroll the world moving forward 
    if player.rect.x >= forwardx_wall:
      scroll = player.rect.x - forwardx_wall
      player.rect.x = forwardx_wall
      
      for sprite in main_group:
        sprite.rect.x -= scroll 
        
      for enemy in enemy_list:  
        enemy.rect.x -= scroll 
        
    # scroll the world moving backward
    if player.rect.x <= backwardx_wall:
      scroll = backwardx_wall - player.rect.x
      player.rect.x = backwardx_wall
      
      for sprite in main_group:
        sprite.rect.x += scroll
        
      for enemy in enemy_list:
        enemy.rect.x += scroll 
        
    player.gravity() 
    player.update() # update player position
    player_list.draw(world)  # <-- draw player
    
    for enemy in enemy_list:
      enemy.update()
    enemy_list.draw(world)
  
  pygame.display.flip()
  clock.tick(FPS)

  for event in pygame.event.get():
      if event.type == pygame.QUIT:
        pygame.quit()
        play_game = False

      if event.type == pygame.KEYDOWN:
        if event.key == ord('q'):
          pygame.quit()
          play_game = False
          
        if event.key == pygame.K_LEFT or event.key == ord('a'):
          player.move(-steps,0)
        if event.key == pygame.K_RIGHT or event.key == ord('d'):
          player.move(steps,0)
        if event.key == pygame.K_UP or event.key == ord('w') or event.key == pygame.K_SPACE:
          player.jump() 
          jump_fx.play()
       

      if event.type == pygame.KEYUP:
        if event.key == pygame.K_LEFT or event.key == ord('a'):
          player.move(steps,0)
        if event.key == pygame.K_RIGHT or event.key == ord('d'):
          player.move(-steps,0) 
    
        if event.key == ord('q'):
          pygame.quit()
          play_game = False
  
  

