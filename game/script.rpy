default current_speaker = None
default player_name = "Jogador"

default lessons_done = set()

default first_trys = 0          
default stress = 0               
default sicredi_seen = set()     


init -10 python:
    import random
    
    def set_speaker(name):
        store.current_speaker = name
        renpy.restart_interaction()

    def blink_dd(open_img, blink_img, min_wait=2.5, max_wait=8.0, blink_time=0.12):
        state = { "next": None, "until": None }

        def _dd(st, at):
            if state["next"] is None:
                state["next"] = st + random.uniform(min_wait, max_wait)

        
            if state["until"] is not None:
                if st < state["until"]:
                    return renpy.displayable(blink_img), 0.0

                state["until"] = None
                state["next"] = st + random.uniform(min_wait, max_wait)
                return renpy.displayable(open_img), 0.0

            if st >= state["next"]:
                state["until"] = st + blink_time
                return renpy.displayable(blink_img), 0.0

            return renpy.displayable(open_img), 0.0

        return DynamicDisplayable(_dd)

    class AutoFocus(object):
        def __init__(self, who):
            self.who = who

        def __call__(self, trans, st, at):
            is_focus = (store.current_speaker == self.who) or (store.current_speaker is None)

            if is_focus:
                trans.alpha = 1.0
                trans.matrixcolor = None
            else:
                trans.alpha = 0.60
                trans.matrixcolor = SaturationMatrix(0.0) * BrightnessMatrix(-0.10)

            return 0.0

    def slide_text(title, subtitle=""):
        if subtitle:
            return "{size=60}{b}%s{/b}{/size}\n{size=30}%s{/size}" % (title, subtitle)
        return "{size=60}{b}%s{/b}{/size}" % (title)



init -5 python:
    renpy.image("iris normal", blink_dd("images/iris/iris normal.png", "images/iris/iris normal_blink.png",
                                        min_wait=3.0, max_wait=7.0, blink_time=0.11))
    renpy.image("iris sad",   blink_dd("images/iris/iris sad.png",   "images/iris/iris normal_blink.png",
                                        min_wait=3.5, max_wait=8.0, blink_time=0.12))

    renpy.image("ace normal", blink_dd("images/ace/ace normal.png",  "images/ace/ace normal_blink.png",
                                        min_wait=2.2, max_wait=5.0, blink_time=0.09))


define i = Character("Iris", callback=lambda ev, **kw: set_speaker("iris") if ev == "begin" else None)
define a = Character("Ace",  callback=lambda ev, **kw: set_speaker("ace")  if ev == "begin" else None)
define l = Character("Luis", callback=lambda ev, **kw: set_speaker("luis") if ev == "begin" else None)
define n = Character(None, callback=lambda ev, **kw: set_speaker("None") if ev == "begin" else None)

transform autofocus(who):
    function AutoFocus(who)

transform char_base:
    zoom 3.5
    yalign 1.0




screen timed_menu(duration=4.0, tick=0.05):

    modal True

    default time_left = duration

    timer tick repeat True action SetScreenVariable("time_left", max(0.0, time_left - tick))

    timer 0.01 repeat True action (Return() if time_left <= 0.0 else NullAction())

    frame:
        style "timed_frame"
        xalign 0.5
        yalign 0.45

        vbox:
            spacing 16
            xalign 0.5

            text "Você tem poucos segundos. Qual é a decisão correta?":
                style "timed_prompt"

            $ frac = time_left / duration if duration > 0 else 0.0

            bar:
                xsize 520
                ysize 18
                value AnimatedValue(
                                        value=frac,
                                        range=1.0,
                                        delay=0.05
                                    )
                left_bar  "gui/bar/custom_left.png"
                right_bar "gui/bar/custom_right.png"

            text "[int(time_left + 0.999)]s":
                size 20
                xalign 0.5
                style "timed_prompt"

            null height 8

            textbutton "Manteve a disciplina":
                style "timed_button"
                text_style "timed_button_text"
                action [
                    SetVariable("timed_choice", "correct"),
                    Return()
                ]

            textbutton "Desistiu e fez tudo pelas coxa":
                style "timed_button"
                text_style "timed_button_text"
                action [
                    SetVariable("timed_choice", "wrong"),
                    Return()
                ]

            textbutton "Fingiu que fazia tudo e não fazia nada":
                style "timed_button"
                text_style "timed_button_text"
                action [
                    SetVariable("timed_choice", "wrong"),
                    Return()
                ]




screen sicredi_hotspots():
    modal True

    frame:
        style "sicredi_frame"
        xalign 0.5
        yalign 0.5

        vbox:
            xalign 0.5
            spacing 18

            text "Clique nos tópicos para ver a evolução:" style "sicredi_title"

            null height 8

            vbox:
                xalign 0.5
                spacing 12

                textbutton "RPA / UiPath":
                    style "sicredi_button"
                    text_style "sicredi_button_text"
                    action Function(sicredi_open_topic, "rpa")
                    sensitive ("rpa" not in sicredi_seen)

                textbutton "Migração para Python":
                    style "sicredi_button"
                    text_style "sicredi_button_text"
                    action Function(sicredi_open_topic, "python")
                    sensitive ("python" not in sicredi_seen)

                textbutton "Sustentação & Observabilidade":
                    style "sicredi_button"
                    text_style "sicredi_button_text"
                    action Function(sicredi_open_topic, "sre")
                    sensitive ("sre" not in sicredi_seen)

            null height 18

            textbutton "Concluir":
                style "sicredi_button"
                text_style "sicredi_confirm_text"
                action Return()
                sensitive (len(sicredi_seen) >= 2)



init -10 python:
    def sicredi_open_topic(topic):
        store.sicredi_seen.add(topic)
        renpy.restart_interaction()

        if topic == "rpa":
            renpy.call_in_new_context("sicredi_topic_rpa")
        elif topic == "python":
            renpy.call_in_new_context("sicredi_topic_python")
        elif topic == "sre":
            renpy.call_in_new_context("sicredi_topic_sre")


label slide(title, subtitle=""):
    show screen slide_screen(title, subtitle)
    pause 2.0
    hide screen slide_screen
    return

screen slide_screen(title, subtitle):
    vbox:
        spacing 8
        xalign 0.5
        yalign 0.5
        text title:
            size 64
            xalign 0.5
            color "#ffffff"
            outlines[(3, "#000000", 0, 0)]

        if subtitle:
            text subtitle:
                size 42
                xalign 0.5
                color "#ffffff"
                outlines[(3, "#000000", 0, 0)]


label sfx_impact(text_sfx="*PORTA BATE*", sound_file="sfx/door_slam.ogg"):
    if renpy.loadable(sound_file):
        play sound sound_file
    show text "{size=60}{b}%s{/b}{/size}" % text_sfx at truecenter
    with hpunch
    pause 0.5
    hide text
    return


label start:
    scene bg room
    jump intro


label intro:
    call slide("Bem-vindo", "Uma apresentação interativa")

    show iris normal at left, char_base, autofocus("iris")
    with moveinleft

    show ace normal at right, char_base, autofocus("ace")
    with moveinright

    i "Oi! Eu sou a Iris."
    a "E eu sou o Ace."
    i "A gente vai te guiar por uma apresentação do nosso criador, Luis, em forma de história."
    a "E no caminho, vamos mostrar mecânicas do Ren'Py."

    jump ask_name




label ask_name:

    $ player_name = renpy.input("Qual é o seu nome?", length=20).strip()
    if not player_name:
        $ player_name = "Jogador"

    i "Prazer, [player_name]!"
    a "Bora começar?"
    menu:
        "Vamos!":
            call sfx_impact("*PORTA BATE*")
            jump chapter_1
        "Não, obrigado.":
            jump sad_ending

label chapter_1:
    call slide("Capítulo 1", "15 anos → Curso Técnico em Informática")

    scene bg school_class
    with wiperight

    show iris normal at left, char_base, autofocus("iris")
    show ace normal at right, char_base, autofocus("ace")

    i "Com 15 anos, Luis entrou no curso técnico em informática."
    a "Adivinha qual foi a área?"

    call quiz_tecnico

    i "Boa!"
    jump chapter_2


label quiz_tecnico:
    $ answered_correctly = False
    $ tries = 0

    while not answered_correctly:
        menu:
            "Técnico em informática":
                $ tries += 1
                $ first_trys += 1
                pause 0.6
                hide text
                $ answered_correctly = True

            "Farmácia":
                $ tries += 1
                $ first_trys += 1
                show iris sad at left, char_base, autofocus("iris")
                i "Sério?"
                if tries >= 2:
                    a "Dica: tem a ver com computador..."
    return

label chapter_2:
    call slide("Capítulo 2", "15–17 → Aprendiz + SENAI (Frimesa)")

    scene bg room
    with dissolve

    show iris normal at left, char_base, autofocus("iris")
    show ace normal at right, char_base, autofocus("ace")

    i "Entre 15 e 17 anos, ele foi Jovem Aprendiz."
    a "Mas não era um 'trabalho normal'…"

    menu:
        "Ele trabalhava direto na fábrica":
            i "Não exatamente."
            a "O foco era formação."
        "Ele fazia curso no SENAI (técnico em informática)":
            a "Isso!"
            i "Era uma parceria da Frimesa com o SENAI para formar técnicos."
        "Ele ficou só estudando em casa":
            i "Também não."
            a "Tinha rotina e compromisso."

    i "Foi uma fase importante pra criar base."
    a "Aí vem o primeiro trabalho 'de verdade'."

    jump chapter_3


label chapter_3:
    call slide("Capítulo 3", "18 → Trabalho integral + Faculdade + TG")

    scene bg school_class
    with fade

    show iris sad at left, char_base, autofocus("iris")
    show ace normal at right, char_base, autofocus("ace")

    i "Com 18 anos, ele foi efetivado na Frimesa como Auxiliar de Logística."
    a "Ah! De setembro de 2023 até março de 2024."
    i "E ao mesmo tempo, começou faculdade à noite…"
    a "…e também foi servir o Exército no Tiro de Guerra de Medianeira!"
    i "Isso foi puxado."

    call timed_choice_demo

    if stress >= 2:
        i "Teve dias que ele sentiu o limite."
    else:
        i "Mesmo cansado, aprendendeu a se organizar."

    a "E aí veio a virada: Sicredi."
    jump chapter_4


label timed_choice_demo:

    $ stress = 0
    $ answered = False

    a "Agora, uma mecânica: decisão com tempo."
    a "Só existe uma escolha correta!"

    while not answered:

        $ timed_choice = None
        call screen timed_menu(duration=4.0)

        if timed_choice is None:
            $ stress += 1
            i "Tempo esgotado."
            a "Na vida real, quando você não escolhe… a rotina escolhe por você."
            a "Tenta de novo."

        elif timed_choice == "wrong":
            $ stress += 1
            i "Não."
            a "Aqui a ideia é mostrar constância. Tenta de novo."

        else:
            i "Isso. Disciplina total."
            a "Perfeito!"
            $ answered = True

    return


label chapter_4:
    call slide("Capítulo 4", "18–20 → Sicredi, RPA e Python")

    scene bg room
    with dissolve

    show iris normal at left, char_base, autofocus("iris")
    show ace normal at right, char_base, autofocus("ace")

    i "Em abril de 2024, ele entrou na Sicredi Vanguarda."
    a "Como Programador Júnior de RPA, usando UiPath."
    i "Mas com o tempo, migrou pra Python..."
    a "E ele migrou junto."

    i "Agora você clica em tópicos pra ver os detalhes."
    $ sicredi_seen = set()
    call screen sicredi_hotspots

    i "Até hoje, o Sicredi foi seu maior ensinamento."
    a "E hoje ele é Analista de Desenvolvimento de Sistemas."
    i "Ele é o ponto focal em manutenção, sustentação e observabilidade."

    jump ending


label sicredi_topic_rpa:
    show iris normal at left, char_base, autofocus("iris")
    i "Ele começou com RPA no UiPath."
    a "Automação de processos, robôs, rotinas repetitivas…"
    i "Foi uma porta de entrada muito forte."
    return

label sicredi_topic_python:
    show ace normal at right, char_base, autofocus("ace")
    a "A tecnologia migrou pra Python com o tempo."
    i "E aí ele foi aprofundando: scripts, integrações, dados…"
    a "E o nível de responsabilidade aumentou."
    return

label sicredi_topic_sre:
    show iris sad at left, char_base, autofocus("iris")
    i "Hoje ele cuida de manutenção e sustentação."
    a "E também observabilidade: monitorar, detectar falhas, garantir saúde do sistema."
    i "É muita responsabilidade para a idade dele? Talvez, mas foi onde ele 'mais 'cresceu."
    return

label ending:
    call slide("Fim", "Obrigado por acompanhar!")

    scene bg room
    with fade

    show iris normal at left, char_base, autofocus("iris")
    show ace normal at right, char_base, autofocus("ace")
    hide iris normal
    hide ace normal

    show luis happy at center, autofocus("luis"), char_base

    l "Essa foi a minha trajetória até aqui, [player_name]."
    l "E tudo isso foi mostrado como uma apresentação interativa em Ren'Py."
    return


label sad_ending:
    scene bg room
    with dissolve

    show iris sad at left, char_base, autofocus("iris")
    show ace normal at right, char_base, autofocus("ace")

    i "Que pena… mas tudo bem."
    a "Se quiser, volte depois pra ver a apresentação completa."
    i "Até a próxima, [player_name]!"

    return
