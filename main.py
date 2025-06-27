from poke_env.player.random_player import RandomPlayer
from poke_env import AccountConfiguration
from poke_env import Player, ShowdownServerConfiguration, LocalhostServerConfiguration, AccountConfiguration
from dotenv import load_dotenv
from learneon import Learneon
import asyncio
import os
import requests


def choseServer():
    chose = input("deseja utilizar o server local?(s/n)")
    if chose == "s" or chose == "S":
        username = os.getenv("SHOWDOWN_USERNAME")
        my_account_config = AccountConfiguration(username, None)
        return my_account_config, LocalhostServerConfiguration
    else:
        username = os.getenv("SHOWDOWN_USERNAME")
        password = os.getenv("SHOWDOWN_TOKEN")
        my_account_config = AccountConfiguration(username=username, password=password)
        return my_account_config, ShowdownServerConfiguration


async def main():
    load_dotenv()
    player_config, server_config = choseServer()
    learneon = Learneon(
        account_configuration=player_config,
        server_configuration=server_config,
        battle_format="gen9randombattle")
    print(f"Player criado: {learneon.username}")
    #aceitarPedido = os.getenv("SHOWDOWN_ACEPET")
    #await learneon.accept_challenges(None, 1)
    await learneon.ladder(1)

    for battle in learneon.battles.values():
        baixar_replay(battle.battle_tag)

    learneon.reset_battles()

def baixar_replay(battle_tag):
    if battle_tag.startswith("battle-"):
        replay_tag = battle_tag[len("battle-"):]
    else:
        replay_tag = battle_tag

    url = f"https://replay.pokemonshowdown.com/{replay_tag}"
    try:
        response = requests.get(url)
        if response.ok and "This replay does not exist" not in response.text:
            with open(f"{replay_tag}.html", "w", encoding="utf-8") as f:
                f.write(response.text)
            print(f"✅ Replay salvo: {replay_tag}.html")
        else:
            print(f"❌ Replay não encontrado: {url}")
    except Exception as e:
        print(f"⚠️ Erro ao baixar replay: {e}")



if __name__ == "__main__":
    asyncio.run(main())

# node pokemon-showdown start --no-security