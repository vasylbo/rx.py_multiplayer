Bacon = require("baconjs")
createView = require("./viewEffects")

connectToServer = (c) ->
  ws = new WebSocket(c.url)
  messages = Bacon
    .fromEventTarget(ws, 'message', (m) -> JSON.parse(m.data))
  messages.ofType = (tp) ->
    @filter((m) -> m?.t == tp)
      .map(".data")
  messages.log("Server:")
  {messages, ws}


logIn = ({messages, ws}) ->
  user = messages.take(1).flatMap(({id, name}) ->
    Bacon.combineTemplate({id, name, ws}))

  newPlayers = messages
    .ofType("new_player")

  updates = messages
    .ofType("up")

  {user, newPlayers, updates}


startGame = (enterFrame, clicks, c) ->
  connection = connectToServer(c)
  {user, newPlayers, updates} = logIn(connection)

  userHero = user
    .sampledBy(newPlayers, (user, hero) -> {user, hero})
    .filter(({user, hero}) -> user.id == hero.id)
    .toProperty()

  view = createView(newPlayers, updates, enterFrame, userHero, c)

  clicks
    .onValue((m) ->
      connection.ws.send(JSON.stringify(m))
    )

  {view}

module.exports = {startGame}