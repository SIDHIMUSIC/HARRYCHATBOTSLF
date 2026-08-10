"""
/eval — Owner only Python code evaluator (Improved)
Usage: /eval print("Hello")
       /eval a = 5\nprint(a * 2)
"""

from telegram.ext import CommandHandler
from config import OWNER_ID
import traceback
import io
from contextlib import redirect_stdout


async def eval_command(update, context):
    # Sirf Owner
    if update.effective_user.id != OWNER_ID:
        return await update.message.reply_text("❌ Sirf Owner use kar sakta hai.")

    if not context.args:
        return await update.message.reply_text(
            "❌ Use like this:\n"
            "`/eval print('Hello')`\n"
            "`/eval 2 + 2`\n"
            "`/eval a = 10\\nprint(a * 5)`",
            parse_mode="Markdown"
        )

    code = " ".join(context.args)

    # \n ko actual new line bana do
    code = code.replace("\\n", "\n")

    stdout = io.StringIO()

    try:
        with redirect_stdout(stdout):
            # Pehle exec try karo (statements ke liye)
            try:
                exec(code, {})
                output = stdout.getvalue()
                
                if output.strip():
                    result_text = f"✅ **Success**\n\n**Output:**\n```\n{output.strip()}\n```"
                else:
                    result_text = "✅ **Success**\n\nCode executed (No output)"
            
            except SyntaxError:
                # Agar expression hai to eval use karo
                result = eval(code)
                result_text = f"✅ **Success**\n\n**Result:**\n`{result}`"

        await update.message.reply_text(result_text, parse_mode="Markdown")

    except Exception:
        error = traceback.format_exc()
        await update.message.reply_text(
            f"❌ **Error**\n\n```\n{error[-1800:]}\n```",
            parse_mode="Markdown"
        )


def register(app):
    app.add_handler(CommandHandler("eval", eval_command))
