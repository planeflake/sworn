"""Fix character_traits to use ARRAY type

Revision ID: fix_character_traits_array
Revises: 114f45c21d96
Create Date: 2024-05-17 23:55:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'fix_character_traits_array'
down_revision: Union[str, None] = '114f45c21d96'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Step 1: Add a temporary column to preserve values
    op.add_column('characters', sa.Column('temp_traits', postgresql.JSONB(), nullable=True))

    # Step 2: Migrate old single enum into an array-compatible format
    op.execute(
        """
        UPDATE characters 
        SET temp_traits = CASE 
            WHEN character_traits IS NOT NULL THEN jsonb_build_array(character_traits)
            ELSE '[]'::jsonb
        END
        """
    )

    # Step 3: Drop old enum column (MUST happen before next step)
    op.drop_column('characters', 'character_traits')

    # Step 4: Recreate as an ARRAY of enum
    op.add_column('characters', sa.Column(
        'character_traits',
        postgresql.ARRAY(
            sa.Enum(
                'DEFENSIVE', 'STRATEGIC', 'ECONOMICAL', 'EXPANSIVE', 'CULTURAL', 'SPIRITUAL',
                name='character_trait_enum',
                create_type=False
            )
        ),
        nullable=True,
        server_default='{}'
    ))

    # Step 5: Now that the column is of array type, restore the data
    op.execute(
        """
        WITH updated_traits AS (
            SELECT 
                id, 
                ARRAY(
                    SELECT jsonb_array_elements_text(temp_traits)::character_trait_enum
                ) AS casted_traits
            FROM characters
            WHERE temp_traits IS NOT NULL
        )
        UPDATE characters
        SET character_traits = updated_traits.casted_traits
        FROM updated_traits
        WHERE characters.id = updated_traits.id
        """
    )

    # Step 6: Drop the temp column
    op.drop_column('characters', 'temp_traits')

def downgrade() -> None:
    # Create a temporary column
    op.add_column('characters', sa.Column('temp_traits', sa.Text(), nullable=True))
    
    # Get the first trait (if any) into the temporary column
    op.execute(
        """
        UPDATE characters
        SET temp_traits = (character_traits[1])::text
        WHERE array_length(character_traits, 1) > 0
        """
    )
    
    # Drop the array column
    op.drop_column('characters', 'character_traits')
    
    # Create the original enum column
    op.add_column('characters', sa.Column('character_traits', 
        sa.Enum('DEFENSIVE', 'STRATEGIC', 'ECONOMICAL', 'EXPANSIVE', 'CULTURAL', 'SPIRITUAL', name='character_trait_enum', create_type=False),
        nullable=True
    ))
    
    # Restore the first trait
    op.execute(
        """
        UPDATE characters
        SET character_traits = temp_traits::character_trait_enum
        WHERE temp_traits IS NOT NULL
        """
    )
    
    # Drop the temporary column
    op.drop_column('characters', 'temp_traits')