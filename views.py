import discord
from database import Session, UserInterest

class PostingView(discord.ui.View):
    def __init__(self, posting_id):
        super().__init__(timeout=None)
        self.posting_id = posting_id

    def already_exists(self, session, post_id, user_id):
        return session.query(UserInterest).filter_by(
        user_id=user_id,
        posting_id=post_id
        ).first()

    @discord.ui.button(label="Interested", style=discord.ButtonStyle.green)
    async def interested_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # what should happen here?
        # hint: you'll want to open a Session, find-or-create a UserInterest row
        # for (interaction.user.id, self.posting_id), set status="interested",
        # commit, then reply to the interaction

        session = Session()

        exists = self.already_exists(session, self.posting_id, str(interaction.user.id))

        if exists:
            exists.status = "interested"
        else:
            new_interest = UserInterest(
            user_id=str(interaction.user.id),
            posting_id=self.posting_id,
            status="interested"
            )

            session.add(new_interest)

        session.commit()
        
        session.close()

        await interaction.response.send_message("Set status to Interested!", ephemeral=True)

    
    