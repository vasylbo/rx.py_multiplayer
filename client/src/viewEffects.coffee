PIXI = require("pixi.js")
Bacon = require("baconjs")

createView = (newOnes, updates, user) ->
  view = new PIXI.Container()

  newOnes.onValue((p) -> addPlayer(view, p))
  updates.onValue((d) -> updatePlayers(view, d))

  view

addPlayer = (container, player) =>
  view = new PIXI.Container()
  view.name = player.id

  gfx = new PIXI.Graphics()
  gfx.name = "graphics"
  gfx.beginFill(0x00ff00)
  gfx.drawCircle(0, 0, player.size)
  gfx.endFill()
  view.addChild(gfx)

  name = new PIXI.Text(player.name)
  view.addChild(name)

  view.x = player.pos.x
  view.y = player.pos.y

  container.addChild(view)
  container

updatePlayers = (container, updates) =>
  doUpdatePlayer(container.getChildByName(id), data) for {id, data} in updates
  container

doUpdatePlayer = (view, info) ->
  console.log("do update", typeof(info))
  switch true
    when typeof info is "object"
      view.x = info.x
      view.y = info.y
      console.log("setting x", view.x, view.y, info.x, info.y)
    else
#      view.scale
      console.log("change size")
module.exports = createView