import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from datetime import datetime

# Configuração de logging para monitorar o funcionamento do bot
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Dicionário de registros de ponto para armazenar dados temporariamente
registros = {}

# Comando para registrar a entrada
async def entrada(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    nome_usuario = update.effective_user.first_name
    horario = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    if user_id not in registros:
        registros[user_id] = {"entrada": [], "saida": []}
    registros[user_id]["entrada"].append(horario)

    await update.message.reply_text(f"{nome_usuario}, sua entrada foi registrada em: {horario}")

# Comando para registrar a saída
async def saida(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    nome_usuario = update.effective_user.first_name
    horario = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    if user_id in registros:
        registros[user_id]["saida"].append(horario)
        await update.message.reply_text(f"{nome_usuario}, sua saída foi registrada em: {horario}")
    else:
        await update.message.reply_text("Você precisa registrar uma entrada antes de registrar uma saída.")

# Comando para visualizar o espelho de ponto
async def espelho(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    nome_usuario = update.effective_user.first_name

    if user_id in registros:
        texto_espelho = f"Espelho de ponto de {nome_usuario}:\n"
        for i, entrada in enumerate(registros[user_id]["entrada"]):
            saida = registros[user_id]["saida"][i] if i < len(registros[user_id]["saida"]) else "Pendente"
            texto_espelho += f"Entrada: {entrada} | Saída: {saida}\n"
        await update.message.reply_text(texto_espelho)
    else:
        await update.message.reply_text("Nenhum registro de ponto encontrado para você.")

# Comando para gerar um relatório diário
async def relatorio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto_relatorio = "Relatório Diário de Pontos:\n"
    for user_id, dados in registros.items():
        nome_usuario = context.bot_data.get(user_id, "Usuário")
        texto_relatorio += f"\n{nome_usuario}:\n"
        for i, entrada in enumerate(dados["entrada"]):
            saida = dados["saida"][i] if i < len(dados["saida"]) else "Pendente"
            texto_relatorio += f"Entrada: {entrada} | Saída: {saida}\n"
    await update.message.reply_text(texto_relatorio)

# Comando para calcular horas extras
async def horas_extras(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    nome_usuario = update.effective_user.first_name

    if user_id in registros:
        horas_extras_total = 0
        for i, entrada in enumerate(registros[user_id]["entrada"]):
            saida = registros[user_id]["saida"][i] if i < len(registros[user_id]["saida"]) else None
            if saida:
                entrada_horario = datetime.strptime(entrada, '%Y-%m-%d %H:%M:%S')
                saida_horario = datetime.strptime(saida, '%Y-%m-%d %H:%M:%S')
                horas_trabalhadas = (saida_horario - entrada_horario).total_seconds() / 3600
                horas_extras_total += max(0, horas_trabalhadas - 8)  # Considerando 8h de jornada padrão
        await update.message.reply_text(f"{nome_usuario}, você tem um total de {horas_extras_total:.2f} horas extras.")
    else:
        await update.message.reply_text("Nenhum registro de ponto encontrado para você.")

# Configuração do bot e comandos
def main():
    application = ApplicationBuilder().token("SEU_TOKEN_DO_TELEGRAM_AQUI").build()

    application.add_handler(CommandHandler("entrada", entrada))
    application.add_handler(CommandHandler("saida", saida))
    application.add_handler(CommandHandler("espelho", espelho))
    application.add_handler(CommandHandler("relatorio", relatorio))
    application.add_handler(CommandHandler("horas_extras", horas_extras))

    application.run_polling()

if __name__ == "__main__":
    main()
